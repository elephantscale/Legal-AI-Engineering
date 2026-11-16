#!/usr/bin/env bash
# resume-deep-dive.sh — rebuild the Core's work tree so the Deep Dive can start.
#
# The Deep Dive (Labs 07, 10 and 12) runs days or weeks after the Core, and every one of its
# labs reads what the Core left in labs/work/:
#
#     catalog.jsonl      Lab 02   the document registry (Lab 10 refuses to start without it)
#     exceptions.jsonl   Lab 02   what failed to extract — Lab 10's memo, Lab 12's audit
#     index.sqlite       Lab 03   the search index Lab 07's workflow runs over
#     chunks.jsonl       Lab 04   chunks and vectors for the RAG stage
#     attestation.json   Lab 05   the egress attestation Lab 12 re-verifies
#
# A student whose laptop was wiped, who switched machines, or who never finished the Core
# cannot start Lab 07. This replays Labs 02–05 offline — no Ollama, no network, no API key —
# and leaves a work tree the Deep Dive labs accept.
#
# TWO DELIBERATE LIMITS, both of them the course working as designed:
#
#   1. It replays the Core labs with THEIR OWN commands. Lab 07's run_matter.py would rebuild
#      the same tree in one line, and that line is the Deep Dive's first lesson.
#   2. It stops before Lab 06's pre-registration. `defensible_review.py protocol` REFUSES to
#      overwrite an existing validation-protocol.md — that refusal is the control, not a bug —
#      and Lab 07's pipeline runs that stage itself. So metrics.json and case-snapshot-*/ are
#      left for Lab 07 to produce at the start of the Deep Dive, which is where the teaching
#      order puts them anyway.
#
#      Note the other direction, which is NOT this script's path: a student who ran the Core
#      back to back (three consecutive days) arrives with Lab 06 genuinely completed, so
#      validation-protocol.md IS on disk. Lab 07's run_matter.py adopts it rather than
#      rebuilding it ([keep], a hash in the ledger, pre_registered stays true). Both routes
#      reach Lab 07; only this one leaves the protocol to be written there.
#
# It is a REPLAY, not your original run: the corpus is rebuilt from the pinned seed, and in
# offline mode the model-shaped steps use the deterministic fallbacks. The artifacts are the
# right shape under the right filenames, which is what Labs 07, 10 and 12 need.
#
#   ./resume-deep-dive.sh                 # ~300 documents, offline, a couple of minutes
#   ./resume-deep-dive.sh --docs 120      # faster
#   ./resume-deep-dive.sh --force         # rebuild even what is already there
#   ./resume-deep-dive.sh --with-ollama   # use the local model instead of the fallbacks
#   ./resume-deep-dive.sh --verbose       # stream each command's output

set -uo pipefail
cd "$(dirname "$0")"
LABS=$(pwd)

# The default seed in assets/make_corpus.py. Pinned here on purpose: the playbooks quote
# document counts and ids from this corpus, so a different seed makes the worked answers wrong.
SEED=20261109

DOCS=300
CORPUS="$LABS/assets/corpus"
WORK="$LABS/work"
FORCE=0
VERBOSE=0
WITH_OLLAMA=0

while [ $# -gt 0 ]; do
  case "$1" in
    --docs) DOCS="$2"; shift 2 ;;
    --corpus) CORPUS=$(realpath -m "$2"); shift 2 ;;
    --work) WORK=$(realpath -m "$2"); shift 2 ;;
    --seed) SEED="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --verbose|-v) VERBOSE=1; shift ;;
    --with-ollama) WITH_OLLAMA=1; shift ;;
    -h|--help) sed -n '2,35p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; DIM=$'\033[2m'; BOLD=$'\033[1m'; OFF=$'\033[0m'

if [ "$WITH_OLLAMA" = 1 ]; then
  unset LEGAL_AI_MODE 2>/dev/null || true
  MODE="local model (whatever your environment provides)"
else
  export LEGAL_AI_MODE=offline
  export LEGAL_AI_EGRESS=deny
  MODE="offline fallbacks (deterministic, and honestly worse — fine for a replay)"
fi

LOG=$(mktemp "${TMPDIR:-/tmp}/resume-deep-dive.XXXXXX.log")
FAILED=0

step() { # step <label> <command...>
  local label="$1"; shift
  printf "  %-46s" "$label"
  if [ "$VERBOSE" = 1 ]; then
    printf "\n"
    if "$@" 2>&1 | tee -a "$LOG"; then printf "  %-46s${GREEN}ok${OFF}\n" ""; return 0; fi
  else
    if "$@" >>"$LOG" 2>&1; then printf "${GREEN}ok${OFF}\n"; return 0; fi
  fi
  printf "${RED}FAILED${OFF}\n"
  FAILED=1
  return 1
}

skip() { printf "  %-46s${DIM}already there, kept${OFF}\n" "$1"; }

# have <glob> — true when the artifact exists and we are not forcing a rebuild
have() { [ "$FORCE" = 0 ] && compgen -G "$1" >/dev/null 2>&1; }

printf "\n${BOLD}Resume the Core, so the Deep Dive can start${OFF}\n"
printf "${DIM}corpus=%s${OFF}\n${DIM}work=%s${OFF}\n${DIM}docs=%s  seed=%s${OFF}\n${DIM}mode=%s${OFF}\n" \
  "$CORPUS" "$WORK" "$DOCS" "$SEED" "$MODE"

# ------------------------------------------------------------------- the corpus
printf "\n${BOLD}Corpus${OFF}\n"
if have "$CORPUS/collection.zip"; then
  skip "corpus ($(basename "$CORPUS")/)"
else
  step "make_corpus.py --docs $DOCS --seed $SEED" \
    python3 "$LABS/assets/make_corpus.py" --out "$CORPUS" --docs "$DOCS" --seed "$SEED" \
    || { printf "\n${RED}Could not build the corpus — nothing downstream will work.${OFF}\n"; exit 1; }
fi

# --------------------------------------------------------------- Lab 02 ingest
printf "\n${BOLD}Lab 02 — ingestion${OFF}\n"
cd "$LABS/02-Ingestion" || exit 1
if have "$WORK/catalog.jsonl"; then skip "catalog.jsonl + exceptions.jsonl"; else
  step "ingest_reference.py --reocr" \
    python3 ingest_reference.py --corpus "$CORPUS" --out "$WORK" --reocr
fi

# --------------------------------------------------------------- Lab 03 search
printf "\n${BOLD}Lab 03 — search${OFF}\n"
cd "$LABS/03-Search" || exit 1
if have "$WORK/index.sqlite"; then skip "index.sqlite"; else
  step "search_index.py build" python3 search_index.py build --work "$WORK"
fi

# ------------------------------------------------------------------ Lab 04 RAG
printf "\n${BOLD}Lab 04 — RAG with citations${OFF}\n"
cd "$LABS/04-Legal-RAG-Citations" || exit 1
if have "$WORK/chunks.jsonl"; then skip "chunks.jsonl"; else
  step "legal_rag.py chunk" python3 legal_rag.py chunk --work "$WORK"
fi
if have "$WORK/vectors.jsonl"; then skip "vectors.jsonl"; else
  step "legal_rag.py embed" python3 legal_rag.py embed --work "$WORK"
fi
if have "$WORK/rag-eval.json"; then skip "rag-eval.json"; else
  step "legal_rag.py eval" python3 legal_rag.py eval --work "$WORK"
fi

# ------------------------------------------------------- Lab 05 egress / proof
printf "\n${BOLD}Lab 05 — local model and egress proof${OFF}\n"
cd "$LABS/05-Local-Model-Egress-Proof" || exit 1
if have "$WORK/attestation.json"; then skip "attestation.json"; else
  step "local_proof.py observe" python3 local_proof.py observe --work "$WORK"
  step "local_proof.py prove"   python3 local_proof.py prove   --work "$WORK"
fi

# ---------------------------------------------- Lab 06, deliberately not replayed
printf "\n${BOLD}Lab 06 — left for Lab 07 to run${OFF}\n"
printf "  ${DIM}%s${OFF}\n" \
  "richness / protocol / classify / measure / bundle are NOT replayed here:" \
  "protocol refuses to overwrite a pre-registration, and that refusal is the" \
  "control rather than a bug. Lab 07's pipeline runs those five stages itself," \
  "so metrics.json and case-snapshot-*/ arrive when you run Lab 07."

# --------------------------------------------------------- what the Deep Dive reads
printf "\n${BOLD}What the Deep Dive will look for${OFF}\n"
MISSING=0
check() { # check <glob> <label> <who needs it>
  if compgen -G "$1" >/dev/null 2>&1; then
    printf "  ${GREEN}✓${OFF} %-22s ${DIM}%s${OFF}\n" "$2" "$3"
  else
    printf "  ${RED}✗${OFF} %-22s ${RED}MISSING${OFF} ${DIM}%s${OFF}\n" "$2" "$3"
    MISSING=1
  fi
}
check "$CORPUS/collection.zip" "corpus"           "every lab reads it"
check "$WORK/catalog.jsonl"    "catalog.jsonl"    "Lab 10 refuses to start without it"
check "$WORK/exceptions.jsonl" "exceptions.jsonl" "Lab 10's memo, Lab 12's audit"
check "$WORK/index.sqlite"     "index.sqlite"     "Lab 07's search stage"
check "$WORK/chunks.jsonl"     "chunks.jsonl"     "Lab 07's chunk/embed stages"
check "$WORK/attestation.json" "attestation.json" "Lab 12 re-verifies it"

printf "\n"
if [ "$FAILED" = 1 ] || [ "$MISSING" = 1 ]; then
  printf "${RED}${BOLD}Not ready.${OFF} Full log: %s\n" "$LOG"
  printf "${DIM}Run it again with --verbose to see which step failed. If you are short of time\n"
  printf "before the Deep Dive starts, --docs 120 builds a smaller corpus.${OFF}\n\n"
  exit 1
fi

printf "${GREEN}${BOLD}Ready.${OFF} The Deep Dive starts at Lab 07:\n\n"
printf "    cd %s/07-Score-and-Package\n" "${LABS/#$HOME/\~}"
printf "    python3 run_matter.py --corpus ../assets/corpus --work ../work\n\n"
printf "${DIM}That command is the Deep Dive's opening point — the Core you just replayed, as one\n"
printf "line with a stage ledger and three human gates. It also produces the two artifacts this\n"
printf "script left alone, metrics.json and the case snapshot, which Lab 12 then audits.${OFF}\n\n"
printf "${YELLOW}Say this out loud if you are teaching from a replayed tree:${OFF} ${DIM}the corpus came\n"
printf "from seed %s, not from the students' own Core run.${OFF}\n\n" "$SEED"
rm -f "$LOG"
