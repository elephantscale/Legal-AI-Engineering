#!/usr/bin/env bash
# test-all-labs.sh — smoke-test every lab end to end, offline.
#
# Runs in LEGAL_AI_MODE=offline so it needs nothing installed beyond Python 3.10+: no
# Ollama, no API key, no network, no Docker. It builds a throwaway corpus and work
# directory under a temp root and deletes them on exit.
#
# This is a STRUCTURAL check, not a grader. It asserts that every lab runs, writes the
# artifact the next lab reads, and exits clean. It deliberately does not assert on the
# quality of offline output — the offline fallbacks are honestly worse and the Teacher's
# Playbooks say so.
#
#   ./test-all-labs.sh              # ~300-document corpus
#   ./test-all-labs.sh --docs 120   # faster
#   ./test-all-labs.sh --keep       # leave the temp tree for inspection
#   ./test-all-labs.sh --verbose    # stream each command's output

set -uo pipefail
cd "$(dirname "$0")"
LABS=$(pwd)

DOCS=300
KEEP=0
VERBOSE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --docs) DOCS="$2"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    --verbose|-v) VERBOSE=1; shift ;;
    -h|--help) sed -n '2,24p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; DIM=$'\033[2m'; BOLD=$'\033[1m'; OFF=$'\033[0m'

export LEGAL_AI_MODE=offline
export LEGAL_AI_EGRESS=deny
unset LEGAL_AI_API_KEY 2>/dev/null || true

ROOT=$(mktemp -d "${TMPDIR:-/tmp}/legal-ai-smoke.XXXXXX")
CORPUS="$ROOT/corpus"
WORK="$ROOT/work"
LOG="$ROOT/run.log"
cleanup() {
  if [ "$KEEP" = 1 ]; then
    printf "\n${DIM}kept: %s${OFF}\n" "$ROOT"
  else
    rm -rf "$ROOT"
  fi
}
trap cleanup EXIT

PASS=0; FAIL=0; SKIP=0
FAILED_STEPS=()

# step <label> <command...>
step() {
  local label="$1"; shift
  printf "  %-46s" "$label"
  if [ "$VERBOSE" = 1 ]; then
    printf "\n"
    if "$@" 2>&1 | tee -a "$LOG" | sed 's/^/      /'; then
      : # pipeline status is tee's; re-check below
    fi
    local rc=${PIPESTATUS[0]}
    printf "  %-46s" ""
  else
    { echo; echo "### $label"; echo "\$ $*"; } >> "$LOG"
    "$@" >> "$LOG" 2>&1
    local rc=$?
  fi
  if [ "$rc" = 0 ]; then
    printf "${GREEN}ok${OFF}\n"; PASS=$((PASS+1)); return 0
  fi
  printf "${RED}FAIL${OFF} (exit %s)\n" "$rc"; FAIL=$((FAIL+1))
  FAILED_STEPS+=("$label")
  return 1
}

# expect_exit <code> <label> <command...>  — for the labs that REFUSE on purpose
expect_exit() {
  local want="$1"; local label="$2"; shift 2
  printf "  %-46s" "$label"
  { echo; echo "### $label (expect exit $want)"; echo "\$ $*"; } >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  if [ "$rc" = "$want" ]; then
    printf "${GREEN}ok${OFF} ${DIM}(refused, exit %s)${OFF}\n" "$rc"; PASS=$((PASS+1)); return 0
  fi
  printf "${RED}FAIL${OFF} (exit %s, wanted %s)\n" "$rc" "$want"; FAIL=$((FAIL+1))
  FAILED_STEPS+=("$label")
  return 1
}

# artifact <path> <label>
artifact() {
  printf "  %-46s" "artifact: $2"
  if [ -s "$1" ]; then
    printf "${GREEN}ok${OFF} ${DIM}(%s)${OFF}\n" "$(wc -c < "$1" | tr -d ' ')"
    PASS=$((PASS+1)); return 0
  fi
  printf "${RED}MISSING${OFF} %s\n" "$1"; FAIL=$((FAIL+1))
  FAILED_STEPS+=("artifact: $2")
  return 1
}

header() { printf "\n${BOLD}%s${OFF}\n" "$1"; }

printf "\n${BOLD}Legal AI Engineering — lab smoke test${OFF}\n"
printf "${DIM}mode=offline  docs=%s  tmp=%s${OFF}\n" "$DOCS" "$ROOT"

# ---------------------------------------------------------------------- corpus
header "Corpus"
step "make_corpus.py --docs $DOCS" \
  python3 "$LABS/assets/make_corpus.py" --out "$CORPUS" --docs "$DOCS" || exit 1
artifact "$CORPUS/collection.zip" "collection.zip"
artifact "$CORPUS/_groundtruth/labels.jsonl" "blind ground truth"
artifact "$CORPUS/production/VOL001.dat" "producer load file"

# ------------------------------------------------------------- 01 ingestion
header "Lab 01 — Ingestion"
cd "$LABS/01-Ingestion"
step "ingest_reference.py --reocr" \
  python3 ingest_reference.py --corpus "$CORPUS" --out "$WORK" --reocr
artifact "$WORK/catalog.jsonl" "catalog.jsonl"
artifact "$WORK/exceptions.jsonl" "exceptions.jsonl (must be non-empty)"
artifact "$WORK/manifest.json" "manifest.json"
step "starter ingest.py runs (TODOs unimplemented)" \
  python3 ingest.py --corpus "$CORPUS" --out "$ROOT/work-starter"
step "--dedupe global" \
  python3 ingest_reference.py --corpus "$CORPUS" --out "$ROOT/work-glob" --dedupe global

# ---------------------------------------------------------------- 02 search
header "Lab 02 — Search"
cd "$LABS/02-Search"
step "search_index.py build" python3 search_index.py build --work "$WORK"
artifact "$WORK/index.sqlite" "index.sqlite"
step "search_index.py search (phrase)" \
  python3 search_index.py search --work "$WORK" -q '"indemnification cap"'
step "search_index.py search (proximity)" \
  python3 search_index.py search --work "$WORK" -q 'indemnif* W/10 cap'
step "search_index.py hitreport" python3 search_index.py hitreport --work "$WORK"
artifact "$WORK/hit-report.json" "hit-report.json"

# ------------------------------------------------------------------- 03 RAG
header "Lab 03 — Legal RAG with citations"
cd "$LABS/03-Legal-RAG-Citations"
step "legal_rag.py chunk" python3 legal_rag.py chunk --work "$WORK"
artifact "$WORK/chunks.jsonl" "chunks.jsonl"
step "legal_rag.py embed" python3 legal_rag.py embed --work "$WORK"
artifact "$WORK/vectors.jsonl" "vectors.jsonl"
artifact "$WORK/vectors-manifest.json" "vectors-manifest.json"
step "legal_rag.py ask" \
  python3 legal_rag.py ask --work "$WORK" -q "What was the indemnification cap in Section 7.3?"
step "verifier catches all three failures" \
  python3 legal_rag.py ask --work "$WORK" -q "What does Section 7.3 say?" --break-citations
step "legal_rag.py eval" python3 legal_rag.py eval --work "$WORK"
artifact "$WORK/rag-eval.json" "rag-eval.json"
artifact "$WORK/rag-log.jsonl" "rag-log.jsonl"

# -------------------------------------------------------- 04 egress / proof
header "Lab 04 — Local model and egress proof"
cd "$LABS/04-Local-Model-Egress-Proof"
step "local_proof.py observe" python3 local_proof.py observe --work "$WORK"
step "local_proof.py prove" python3 local_proof.py prove --work "$WORK"
artifact "$WORK/attestation.json" "attestation.json"
step "local_proof.py tripwire (leaks blocked)" python3 local_proof.py tripwire --work "$WORK"
step "local_proof.py compare (cloud row skipped)" python3 local_proof.py compare --work "$WORK"
artifact "$WORK/local-vs-cloud.json" "local-vs-cloud.json"

# ------------------------------------------------------ 05 defensible review
header "Lab 05 — Defensible review"
cd "$LABS/05-Defensible-Review"
step "richness (prevalence first)" python3 defensible_review.py richness --work "$WORK" --corpus "$CORPUS"
step "protocol (pre-register, hashed)" \
  python3 defensible_review.py protocol --work "$WORK" --corpus "$CORPUS"
artifact "$WORK/validation-protocol.md" "validation-protocol.md"
step "classify" python3 defensible_review.py classify --work "$WORK" --corpus "$CORPUS"
artifact "$WORK/decisions.jsonl" "decisions.jsonl"
step "measure (recall/elusion/precision)" python3 defensible_review.py measure --work "$WORK" --corpus "$CORPUS"
artifact "$WORK/metrics.json" "metrics.json"
step "bundle (case snapshot)" python3 defensible_review.py bundle --work "$WORK" --corpus "$CORPUS"
step "verify (does it replay?)" python3 defensible_review.py verify --work "$WORK" --corpus "$CORPUS"
SNAP="$WORK/case-snapshot-SYNTHETIC-DEMO-01"
artifact "$SNAP/manifest.json" "bundle: manifest.json (every pin)"
artifact "$SNAP/validation/protocol.md" "bundle: validation/protocol.md"
artifact "$SNAP/validation/metrics.json" "bundle: validation/metrics.json"
artifact "$SNAP/attestation.json" "bundle: attestation.json"
artifact "$SNAP/VERIFY.md" "bundle: VERIFY.md"
artifact "$SNAP/verification.json" "bundle: verification.json"

# ------------------------------------------------------- 06 score & package
header "Lab 06 — Score and package"
cd "$LABS/06-Score-and-Package"
step "run_matter.py (12 stages, one command)" \
  python3 run_matter.py --corpus "$CORPUS" --work "$ROOT/work-matter"
expect_exit 2 "produce REFUSES without approval" \
  python3 run_matter.py --work "$ROOT/work-matter" --stage produce
step "record human approval" \
  python3 run_matter.py --work "$ROOT/work-matter" --approve-production "Smoke Test, Esq."
step "produce (approved)" python3 run_matter.py --work "$ROOT/work-matter" --stage produce
artifact "$ROOT/work-matter/production/VOL001/VOL001.dat" "production load file"
step "--resume re-runs nothing when complete" \
  python3 run_matter.py --corpus "$CORPUS" --work "$ROOT/work-matter" --resume
step "sais100.py --save-baseline" \
  python3 sais100.py --work "$ROOT/work-matter" --save-baseline
step "sais100.py --delta" \
  python3 sais100.py --work "$ROOT/work-matter" --delta --out "$ROOT/sais100-score.json"
artifact "$ROOT/sais100-score.json" "sais100-score.json"

# ----------------------------------------------------------------- 07 capstone
header "Lab 07 — Capstone"
printf "  %-46s${YELLOW}n/a${OFF} ${DIM}(assembly + rubric; nothing to execute)${OFF}\n" "README + rubric"
SKIP=$((SKIP+1))

# --------------------------------------------------------- 08 investigations
header "Lab 08 — Investigations and timeline"
cd "$LABS/08-Investigations-Timeline"
step "investigate.py entities" python3 investigate.py entities --work "$WORK"
artifact "$WORK/entities.jsonl" "entities.jsonl"
step "investigate.py resolve" python3 investigate.py resolve --work "$WORK"
step "investigate.py threads" python3 investigate.py threads --work "$WORK"
artifact "$WORK/threads.jsonl" "threads.jsonl"
artifact "$WORK/dropped_recipients.jsonl" "dropped_recipients.jsonl"
step "investigate.py timeline --responsive" \
  python3 investigate.py timeline --work "$WORK" --responsive
step "investigate.py diff" python3 investigate.py diff --work "$WORK"
step "investigate.py leads" python3 investigate.py leads --work "$WORK"
artifact "$WORK/collection_leads.jsonl" "collection_leads.jsonl"

# ------------------------------------------------------------- 09 agentic
header "Lab 09 — Agentic legal workflow"
cd "$LABS/09-Agentic-Legal-Workflow"
step "agent.py tools (closed registry)" python3 agent.py tools --work "$WORK"
step "agent.py run" python3 agent.py run --work "$WORK"
for atk in $(python3 -c "import agent,sys; print(' '.join(sorted(agent.ATTACKS)))" 2>/dev/null); do
  step "attack blocked: $atk" python3 agent.py run --work "$WORK" --attack "$atk"
done
artifact "$WORK/exception_memo.md" "exception_memo.md (UNAPPROVED draft)"
artifact "$WORK/steps.jsonl" "steps.jsonl (the refusal log)"
step "agent.py approve (gate recorded)" \
  python3 agent.py approve --work "$WORK" --by "Smoke Test, Esq."
artifact "$WORK/approvals.jsonl" "approvals.jsonl"

# ---------------------------------------------------------------- 10 scale
header "Lab 10 — Deploy at scale"
cd "$LABS/10-Deploy-At-Scale"
export LAB10_WORK_ROUNDS=50          # keep the smoke test fast; the curve needs 1500
step "work_queue.py init" \
  python3 work_queue.py init --work "$ROOT/work-queue" --corpus "$CORPUS"
step "work_queue.py run --workers 2" \
  python3 work_queue.py run --work "$ROOT/work-queue" --workers 2
step "work_queue.py status" python3 work_queue.py status --work "$ROOT/work-queue"
step "lease recovery: --kill-one then reap" \
  bash -c "python3 work_queue.py init --work '$ROOT/work-kill' --corpus '$CORPUS' \
           && python3 work_queue.py run --work '$ROOT/work-kill' --workers 2 --kill-one \
           ; python3 work_queue.py reap --work '$ROOT/work-kill'"
unset LAB10_WORK_ROUNDS
step "destroy_matter.py plan" \
  python3 destroy_matter.py plan --work "$WORK" --matter SYNTHETIC-DEMO-01
step "destroy --list-only (nothing deleted)" \
  python3 destroy_matter.py destroy --work "$WORK" --matter SYNTHETIC-DEMO-01 \
    --confirm SYNTHETIC-DEMO-01 --by "Smoke Test, Esq." --list-only
expect_exit 2 "destroy REFUSES without --confirm" \
  python3 destroy_matter.py destroy --work "$WORK" --matter SYNTHETIC-DEMO-01 \
    --by "Smoke Test, Esq."
expect_exit 2 "destroy REFUSES without --by" \
  python3 destroy_matter.py destroy --work "$WORK" --matter SYNTHETIC-DEMO-01 \
    --confirm SYNTHETIC-DEMO-01

# ------------------------------------------------------------ 11 governance
header "Lab 11 — Governance audit"
cd "$LABS/11-Governance-Audit"
step "audit.py artifacts" python3 audit.py artifacts --work "$ROOT/work-matter"
step "audit.py audit (verified score)" python3 audit.py audit --work "$ROOT/work-matter"
step "audit.py findings" python3 audit.py findings --work "$ROOT/work-matter"
artifact "$ROOT/work-matter/audit-findings.md" "audit-findings.md"
step "audit.py delta" python3 audit.py delta --work "$ROOT/work-matter"
step "guard: nonexistent work dir fails cleanly" \
  bash -c "python3 audit.py audit --work '$ROOT/nope' 2>&1 | grep -qi 'run_matter\|not found\|no such'"

# ------------------------------------------------- destruction, run LAST
header "Lab 10 — destruction (runs last: it deletes the shared work dir)"
cd "$LABS/10-Deploy-At-Scale"
step "destroy --confirm --by" \
  python3 destroy_matter.py destroy --work "$WORK" --matter SYNTHETIC-DEMO-01 \
    --confirm SYNTHETIC-DEMO-01 --by "Smoke Test, Esq."
step "verify after destruction" \
  python3 destroy_matter.py verify --work "$WORK" --matter SYNTHETIC-DEMO-01

# ------------------------------------------------------------------- report
printf "\n${BOLD}Result${OFF}\n"
printf "  %d passed, %d failed, %d n/a\n" "$PASS" "$FAIL" "$SKIP"
if [ "$FAIL" -gt 0 ]; then
  printf "\n  ${RED}Failed:${OFF}\n"
  for s in "${FAILED_STEPS[@]}"; do printf "    - %s\n" "$s"; done
  printf "\n  Full output: %s\n" "$LOG"
  printf "  ${DIM}(re-run with --keep --verbose to inspect)${OFF}\n\n"
  KEEP=1
  exit 1
fi
printf "  ${GREEN}All labs run offline, in order, and produce their deliverables.${OFF}\n\n"
