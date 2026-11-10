# `labs/common/` — the shared chokepoints

Four small modules the labs import. They exist here, rather than being copy-pasted into
each lab, for the same reason FreeEed keeps its AI access in two functions: **if every
call to a model goes through one place, "go local" is a config change instead of a
migration.**

| Module | What it is | Taught in |
|---|---|---|
| `llm.py` | The **only** place a model or embedder is called. Local by default; deterministic offline fallback; a cloud toggle for the contrast case. | Modules 4, 5 |
| `egress.py` | In-process egress guard (default-deny sockets, loopback allowed) + the attestation writer. | Module 5 |
| `metrics.py` | TAR metrics — recall, elusion, precision, richness — with Wilson confidence intervals and sample sizing. | Module 6 |
| `bundle.py` | Reads/writes the reproducibility bundle ("defensible case snapshot") and verifies a replay. | Module 6 |

Labs import them with:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "common"))
from llm import chat, embed, model_info
```

## The design rule worth copying

`llm.py` has exactly two public entry points that touch a model: `chat()` and `embed()`.
Nothing else in any lab calls an AI endpoint. That is why Lab 04 can make the whole stack
local by changing two environment variables, and why the attestation in Lab 04 can
enumerate every AI component honestly — there are only two.

Centralize your model client on day one, even when you only ever plan to use one provider.
