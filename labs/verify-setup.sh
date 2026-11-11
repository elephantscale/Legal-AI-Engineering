#!/usr/bin/env bash
# verify-setup.sh — what you have, what you are missing, and what each gap COSTS you.
#
# This script never fails the class. Everything it reports as missing has a fallback, and
# it tells you which lesson the fallback degrades. That is the honest version of a setup
# check: a red cross with no consequence attached teaches nothing.

set -uo pipefail
cd "$(dirname "$0")"

GREEN=$'\033[32m'; YELLOW=$'\033[33m'; DIM=$'\033[2m'; BOLD=$'\033[1m'; OFF=$'\033[0m'
ok()   { printf "  ${GREEN}yes${OFF}   %-26s %s\n" "$1" "${2-}"; }
warn() { printf "  ${YELLOW}no ${OFF}   %-26s %s\n" "$1" "${2-}"; }
note() { printf "        ${DIM}%s${OFF}\n" "$1"; }

printf "\n${BOLD}Legal AI Engineering — environment${OFF}\n\n"

# ------------------------------------------------------------------------ required
printf "${BOLD}Required${OFF}\n"
PY=$(command -v python3 || true)
if [ -n "$PY" ]; then
  V=$(python3 -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])')
  MAJ=$(python3 -c 'import sys;print(sys.version_info[0])')
  MIN=$(python3 -c 'import sys;print(sys.version_info[1])')
  if [ "$MAJ" -ge 3 ] && [ "$MIN" -ge 10 ]; then
    ok "python3" "$V"
  else
    warn "python3" "$V — need 3.10+"
    note "The labs use match-free but modern syntax: X | None annotations and dataclasses."
  fi
else
  warn "python3" "not found"
  note "Nothing works without this. Install Python 3.10 or newer."
fi
printf "\n"

# ------------------------------------------------------------------------ optional
printf "${BOLD}Optional — each gap has a fallback, and a cost${OFF}\n"

if python3 -c 'import pypdf' 2>/dev/null; then
  ok "pypdf" "$(python3 -c 'import pypdf;print(pypdf.__version__)' 2>/dev/null)"
else
  warn "pypdf" "pip install pypdf==5.1.0"
  note "Lab 02: PDFs become exceptions instead of text. The lab still runs — and an"
  note "exception list with real entries is the lab's actual lesson — but you will not"
  note "see the PDF extraction path."
fi

if python3 -c 'import PIL' 2>/dev/null; then
  ok "Pillow" "$(python3 -c 'import PIL;print(PIL.__version__)' 2>/dev/null)"
else
  warn "Pillow" "pip install Pillow==11.0.0"
  note "make_corpus.py cannot render the synthetic scans, so the OCR thread in Labs 02"
  note "and 02 is missing — including the indemnif1cation finding, which is the best"
  note "thirty seconds of Day 1. Install this one if you install nothing else."
fi

if python3 -c 'import requests' 2>/dev/null; then
  ok "requests" "$(python3 -c 'import requests;print(requests.__version__)' 2>/dev/null)"
else
  warn "requests" "pip install requests==2.32.3"
  note "No local model and no Tika. Labs fall back to offline mode automatically."
fi

if command -v tesseract >/dev/null 2>&1; then
  ok "tesseract" "$(tesseract --version 2>&1 | head -1)"
else
  warn "tesseract" "apt install tesseract-ocr tesseract-ocr-eng / brew install tesseract"
  note "Lab 02 --reocr does nothing, so the producer's OCR sidecar is all you have."
  note "You lose the three-different-hit-counts exercise in Lab 03. The scans stay as"
  note "exceptions, which is itself a defensible outcome — say so in your memo."
fi

if command -v docker >/dev/null 2>&1; then
  ok "docker" "$(docker --version 2>/dev/null | head -1)"
else
  warn "docker" "optional"
  note "Labs 07 and 11 Part 4 (compose, internal: true) become a read-the-file exercise."
  note "Nothing downstream depends on it; the score and the production set do not."
fi
printf "\n"

# -------------------------------------------------------------------- local model
printf "${BOLD}Local model${OFF}\n"
BASE="${LEGAL_AI_BASE_URL:-http://localhost:11434/v1}"
MODEL="${LEGAL_AI_MODEL:-qwen3:8b}"
EMBED="${LEGAL_AI_EMBED:-nomic-embed-text}"
if python3 - <<PY 2>/dev/null
import json, urllib.request, sys
base = "${BASE}".rstrip("/")
try:
    with urllib.request.urlopen(base + "/models", timeout=3) as r:
        json.load(r)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
then
  ok "endpoint" "$BASE"
  TAGS=$(python3 - <<PY 2>/dev/null
import json, urllib.request
root = "${BASE}".rstrip("/").removesuffix("/v1")
try:
    with urllib.request.urlopen(root + "/api/tags", timeout=3) as r:
        print(" ".join(m["name"] for m in json.load(r).get("models", [])))
except Exception:
    print("")
PY
)
  for want in "$MODEL" "$EMBED"; do
    if printf '%s' "$TAGS" | tr ' ' '\n' | grep -qx -- "$want" \
       || printf '%s' "$TAGS" | tr ' ' '\n' | grep -q "^${want%%:*}"; then
      ok "model" "$want"
    else
      warn "model" "$want not pulled"
      note "ollama pull $want"
    fi
  done
else
  warn "endpoint" "$BASE unreachable"
  note "Set LEGAL_AI_MODE=offline and every lab still completes with deterministic"
  note "stdlib fallbacks. What you lose: real model output in Labs 04 and 06, and the"
  note "chance to see a local model lose to a cloud model in front of you. What you"
  note "keep: all seven planted findings, every guardrail, every metric, every"
  note "artifact. The offline paths are honestly worse and each one says so."
fi
printf "\n"

# ------------------------------------------------------------------------- corpus
printf "${BOLD}Corpus${OFF}\n"
if [ -f assets/corpus/collection.zip ]; then
  N=$(ls assets/corpus 2>/dev/null | wc -l | tr -d ' ')
  ok "assets/corpus" "$N top-level entries"
  if [ -f assets/corpus/_groundtruth/labels.jsonl ]; then
    L=$(wc -l < assets/corpus/_groundtruth/labels.jsonl | tr -d ' ')
    ok "ground truth" "$L labels — Lab 06 needs these"
  else
    warn "ground truth" "missing"
    note "Regenerate: python3 assets/make_corpus.py"
  fi
else
  warn "assets/corpus" "not generated"
  note "python3 assets/make_corpus.py            (~1200 documents)"
  note "python3 assets/make_corpus.py --docs 300 (faster; every lesson still lands)"
fi
printf "\n"

# --------------------------------------------------------------------- the verdict
MODE="${LEGAL_AI_MODE:-local}"
printf "${BOLD}Verdict${OFF}\n"
if [ -z "$PY" ]; then
  printf "  Install Python 3.10+ and run this again.\n\n"
  exit 1
fi
printf "  LEGAL_AI_MODE=%s\n" "$MODE"
printf "  You can run every lab. Nothing above is blocking.\n"
printf "  ${DIM}No API key is needed anywhere in this course, and no lab requires the\n"
printf "  network. If a lab ever asks you for either, that is a bug — report it.${OFF}\n\n"
