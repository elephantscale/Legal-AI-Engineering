"""egress.py — the in-process egress guard and the attestation writer.

Module 5's three layers, as code you can actually run in a lab:

    1. ENFORCE  — install a socket guard: default-deny, loopback (and optionally the LAN)
                  allowed. Every attempt is recorded, allowed or blocked.
    2. OBSERVE  — the recorder keeps every connection attempt for the run window.
    3. ATTEST   — write attestation.json: the window, the AI components, the connection
                  log, and the explicit claim.

Honest scope, stated here and in every artifact this module writes:

  * This guard is **in-process**. It covers socket calls made by THIS Python process
    (and anything using the stdlib socket module inside it). It does not cover
    subprocesses, other processes on the host, or anything below the Python runtime.
  * A production deployment pairs this with real enforcement — a firewall rule, an
    `internal: true` Docker network, or an isolated subnet. The guard demonstrates the
    principle and produces the artifact; the firewall is what actually stops a packet.
  * DNS resolution is itself a disclosure. The guard counts and blocks it too.

Say all of that out loud rather than letting an opposing expert say it for you. A narrow
claim with an artifact behind it beats a broad claim with a brochure behind it.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ATTESTATION_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class EgressBlocked(OSError):
    """Raised when the guard refuses an outbound connection."""


@dataclass
class Attempt:
    when: str
    host: str
    port: int | None
    kind: str          # "connect" | "resolve"
    allowed: bool
    reason: str

    def as_dict(self) -> dict:
        return {"when": self.when, "peer": f"{self.host}:{self.port}" if self.port
                else self.host, "kind": self.kind, "allowed": self.allowed,
                "reason": self.reason}


@dataclass
class EgressGuard:
    """Default-deny socket guard with a recorder.

    policy:
      "deny"        loopback only. Everything else raises EgressBlocked. (the default)
      "deny-lan"    loopback + RFC1918 private ranges allowed (for a server deployment
                    where Ollama/Tika/Solr live on the LAN)
      "observe"     allow everything, but record it. Use this FIRST, on a system you did
                    not build, to find out what it actually does.
    """
    policy: str = "deny"
    attempts: list[Attempt] = field(default_factory=list)
    started: str = field(default_factory=_now)
    ended: str | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _orig_connect: Any = field(default=None, repr=False)
    _orig_getaddrinfo: Any = field(default=None, repr=False)
    _installed: bool = False

    # ---------------------------------------------------------------- policy
    def _verdict(self, host: str) -> tuple[bool, str]:
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            # a hostname, not an address: localhost is fine, anything else is a lookup
            if host in ("localhost", "localhost.localdomain", "ip6-localhost"):
                return True, "loopback hostname"
            if self.policy == "observe":
                return True, "observe mode: allowed and recorded"
            return False, "hostname is not loopback"
        if ip.is_loopback:
            return True, "loopback"
        if self.policy == "observe":
            return True, "observe mode: allowed and recorded"
        if self.policy == "deny-lan" and ip.is_private:
            return True, "private range, deny-lan policy"
        return False, f"non-loopback address under policy '{self.policy}'"

    def _record(self, host: str, port: int | None, kind: str) -> tuple[bool, str]:
        allowed, reason = self._verdict(host)
        with self._lock:
            self.attempts.append(Attempt(_now(), host, port, kind, allowed, reason))
        return allowed, reason

    # ---------------------------------------------------------------- install
    def install(self) -> "EgressGuard":
        if self._installed:
            return self
        self._orig_connect = socket.socket.connect
        self._orig_getaddrinfo = socket.getaddrinfo
        guard = self

        def connect(sock_self, address, *a, **kw):  # noqa: ANN001
            host, port = (address[0], address[1]) if isinstance(address, tuple) \
                else (str(address), None)
            allowed, reason = guard._record(str(host), port, "connect")
            if not allowed:
                raise EgressBlocked(
                    f"EGRESS BLOCKED: connect to {host}:{port} — {reason}. "
                    f"This is the guard working, not a bug.")
            return guard._orig_connect(sock_self, address, *a, **kw)

        def getaddrinfo(host, port, *a, **kw):  # noqa: ANN001
            # Note: create_connection() calls this even for a bare IP literal, so we
            # distinguish a real name lookup from an address pass-through. Both are
            # recorded; only a name lookup is a *disclosure to a resolver*.
            is_literal = _is_ip_literal(str(host))
            kind = "connect" if is_literal else "resolve"
            allowed, reason = guard._record(str(host), port if isinstance(port, int)
                                            else None, kind)
            if not allowed:
                detail = (f"connection to {host}" if is_literal
                          else f"DNS lookup for {host}")
                hint = ("" if is_literal else
                        " A lookup is itself a disclosure: it tells a resolver what you "
                        "are working on, and when.")
                raise EgressBlocked(f"EGRESS BLOCKED: {detail} — {reason}.{hint}")
            return guard._orig_getaddrinfo(host, port, *a, **kw)

        socket.socket.connect = connect       # type: ignore[method-assign]
        socket.getaddrinfo = getaddrinfo      # type: ignore[assignment]
        self._installed = True
        return self

    def uninstall(self) -> None:
        if not self._installed:
            return
        socket.socket.connect = self._orig_connect    # type: ignore[method-assign]
        socket.getaddrinfo = self._orig_getaddrinfo   # type: ignore[assignment]
        self._installed = False
        self.ended = _now()

    def __enter__(self) -> "EgressGuard":
        return self.install()

    def __exit__(self, *exc: object) -> None:
        self.uninstall()

    # ---------------------------------------------------------------- summary
    def summary(self) -> dict:
        peers: dict[str, dict] = {}
        for a in self.attempts:
            key = f"{a.host}:{a.port}" if a.port else a.host
            row = peers.setdefault(key, {"peer": key, "kind": a.kind, "count": 0,
                                         "allowed": a.allowed,
                                         "loopback": _is_loopback(a.host),
                                         "reason": a.reason})
            row["count"] += 1
        return {"by_peer": sorted(peers.values(), key=lambda r: -r["count"])}

    @property
    def non_loopback(self) -> int:
        """The number that goes in the attestation. Loopback does not count."""
        return sum(1 for a in self.attempts if not _is_loopback(a.host))

    @property
    def blocked(self) -> int:
        return sum(1 for a in self.attempts if not a.allowed)


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_loopback(host: str) -> bool:
    if host in ("localhost", "localhost.localdomain", "ip6-localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


# ------------------------------------------------------------------- attestation
def write_attestation(path: str | Path, *, guard: EgressGuard, matter: str,
                      ai_components: dict, documents_processed: int,
                      extra: dict | None = None) -> Path:
    """Emit the artifact from Module 5. Returns the path written."""
    path = Path(path)
    non_loopback = [a.as_dict() for a in guard.attempts if not _is_loopback(a.host)]
    doc = {
        "attestation_version": ATTESTATION_VERSION,
        "run_id": f"run-{guard.started}-{os.getpid():x}",
        "matter": matter,
        "window": {"start": guard.started, "end": guard.ended or _now()},
        "host": {
            "platform": sys.platform,
            "python": sys.version.split()[0],
            # hashed, not named: the hostname is not the course's business
            "hostname_sha256": hashlib.sha256(
                socket.gethostname().encode()).hexdigest(),
        },
        "ai_components": ai_components,
        "egress_policy": {
            "deny": "default-deny; loopback only",
            "deny-lan": "default-deny; loopback + RFC1918 private ranges",
            "observe": "OBSERVE ONLY — nothing was enforced",
        }.get(guard.policy, guard.policy),
        "connections_observed": guard.summary()["by_peer"],
        "connection_attempts_total": len(guard.attempts),
        "blocked_attempts": guard.blocked,
        "non_loopback_connections": len(non_loopback),
        "non_loopback_detail": non_loopback,
        "documents_processed": documents_processed,
        "claim": ("No document content left this host during the window above."
                  if not non_loopback else
                  "DOCUMENT CONTENT MAY HAVE LEFT THIS HOST — see non_loopback_detail."),
        "scope_and_limits": [
            "In-process guard: covers socket calls made by this Python process only.",
            "Does not cover subprocesses, other host processes, or kernel-level paths.",
            "Covers the time window stated above, not continuous operation.",
            "DNS lookups are counted as disclosures and are included above.",
            "Enforcement in production belongs to a firewall or an isolated network; "
            "this guard demonstrates the control and produces the record.",
        ],
        "produced_by": "egress.py (Legal AI Engineering, Elephant Scale)",
    }
    if extra:
        doc.update(extra)
    body = json.dumps(doc, indent=2, sort_keys=False)
    # the artifact hashes its own content, so tampering is detectable
    doc["artifact_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------- demo
if __name__ == "__main__":
    print("Demonstrating the guard. Loopback is allowed; anything else is blocked.\n")
    with EgressGuard(policy="deny") as g:
        try:
            s = socket.create_connection(("127.0.0.1", 11434), timeout=0.2)
            s.close()
            print("  loopback :11434 -> connected (something is listening)")
        except EgressBlocked as e:
            print(f"  loopback -> UNEXPECTEDLY BLOCKED: {e}")
        except OSError:
            print("  loopback :11434 -> allowed by the guard, nothing listening")
        try:
            socket.create_connection(("93.184.216.34", 443), timeout=1)
            print("  external -> CONNECTED. The guard is not working.")
        except EgressBlocked as e:
            print(f"  external -> BLOCKED, as designed\n             {e}")
        try:
            socket.getaddrinfo("api.openai.com", 443)
            print("  dns      -> RESOLVED. The guard is not working.")
        except EgressBlocked as e:
            print(f"  dns      -> BLOCKED, as designed\n             {e}")
    print(f"\n  attempts recorded: {len(g.attempts)}   blocked: {g.blocked}   "
          f"non-loopback: {g.non_loopback}")
