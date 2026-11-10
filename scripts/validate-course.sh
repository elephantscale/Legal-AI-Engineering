#!/usr/bin/env bash
# validate-course.sh — repository structure and house-style check for Legal AI Engineering.
#
# Structural only. It does not run the labs — that is labs/test-all-labs.sh — and it does
# not assemble the decks, which Mark builds himself. Keep it green.

set -u
if [ -t 1 ]; then G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[33m'; B=$'\e[1m'; D=$'\e[2m'; N=$'\e[0m'
else G=; R=; Y=; B=; D=; N=; fi
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
WARN=0
ok()   { printf "  ${G}PASS${N}  %s\n" "$1"; }
bad()  { printf "  ${R}FAIL${N}  %s\n" "$1"; FAIL=$((FAIL+1)); }
warn() { printf "  ${Y}WARN${N}  %s\n" "$1"; WARN=$((WARN+1)); }

printf "${B}Legal AI Engineering — course repo validation${N}\n"

# ------------------------------------------------------------------ required files
required=(
  README.md outline.md CLAUDE.md OPERATIONS.md .gitignore
  slides/slide-list.txt slides/gen.sh slides/README.md slides/00-about.md
  labs/README.md labs/SETUP.md labs/verify-setup.sh labs/test-all-labs.sh
  labs/.env.example labs/requirements-all.txt
  labs/assets/make_corpus.py
  labs/common/README.md labs/common/llm.py labs/common/egress.py
  labs/common/metrics.py labs/common/bundle.py
  course-materials/README.md
  course-materials/legal-ai-design-canvas.md
  course-materials/defensibility-checklist.md
  course-materials/tar-metrics-cheatsheet.md
  course-materials/privilege-and-egress-attestation.md
  course-materials/reproducibility-manifest-template.md
  course-materials/sais-100-legal-overlay.md
  course-materials/capstone-rubric.md
  scripts/validate-course.sh
)
printf "\n${B}Required files${N}\n"
for f in "${required[@]}"; do
  [ -f "$ROOT_DIR/$f" ] && ok "$f" || bad "$f missing"
done

printf "\n${B}Executable${N}\n"
for f in labs/verify-setup.sh labs/test-all-labs.sh scripts/validate-course.sh slides/gen.sh; do
  if [ -x "$ROOT_DIR/$f" ]; then ok "$f is executable"; else bad "$f is not executable"; fi
done

# ------------------------------------------------------------------------- slides
printf "\n${B}Slides${N}\n"
MANIFEST="$ROOT_DIR/slides/slide-list.txt"
while IFS= read -r deck; do
  [ -z "$deck" ] && continue
  [ -f "$ROOT_DIR/slides/$deck" ] && ok "deck $deck" || bad "deck $deck in slide-list.txt but missing"
done < "$MANIFEST"

# every deck on disk is in the manifest
for d in "$ROOT_DIR"/slides/[0-9][0-9]-*.md; do
  b=$(basename "$d")
  grep -qxF "$b" "$MANIFEST" || bad "deck $b on disk but not in slide-list.txt"
done

# modules 01-12 plus 00-about
for n in 00 01 02 03 04 05 06 07 08 09 10 11 12; do
  ls "$ROOT_DIR"/slides/${n}-*.md >/dev/null 2>&1 || bad "no deck numbered $n"
done

printf "\n${B}Slide house style${N}\n"
for d in "$ROOT_DIR"/slides/[0-9][0-9]-*.md; do
  b=$(basename "$d")
  # title slide: an H1 and 'Elephant Scale' near the top
  head -8 "$d" | grep -q '^# ' || bad "$b has no H1 title slide"
  head -8 "$d" | grep -q 'Elephant Scale' || bad "$b title slide does not say Elephant Scale"
  # slide separators
  grep -q '^---$' "$d" || bad "$b has no --- slide separators"
  # instructor narration
  grep -q '^Notes:' "$d" || warn "$b has no Notes: narration blocks"
  # the visual beat
  grep -q '^> ' "$d" || warn "$b has no > blockquote takeaways"
  # content decks hand off to a lab (00-about is the exception)
  # 00-about has no module; 01 is the framing module with no lab of its own; 08 IS the
  # capstone deck, and Lab 07 is the capstone it hands off to by name in the body.
  case "$b" in
    00-about.md|01-*|08-capstone.md) ;;
    *) grep -qiE '^## (▶ )?.*Lab [0-9]' "$d" || bad "$b has no Lab NN hand-off slide" ;;
  esac
  # image tags stay simple: src + width only
  if grep -o '<img [^>]*>' "$d" 2>/dev/null | grep -qv 'style="width'; then
    grep -o '<img [^>]*>' "$d" | grep -v 'style="width' | while read -r tag; do
      warn "$b image tag should be src + width only: $tag"
    done
  fi
done

# ---------------------------------------------------------------------------- labs
printf "\n${B}Labs${N}\n"
expected_labs=(
  01-Ingestion 02-Search 03-Legal-RAG-Citations 04-Local-Model-Egress-Proof
  05-Defensible-Review 06-Score-and-Package 07-Capstone
  08-Investigations-Timeline 09-Agentic-Legal-Workflow 10-Deploy-At-Scale
  11-Governance-Audit
)
for lab in "${expected_labs[@]}"; do
  [ -f "$ROOT_DIR/labs/$lab/README.md" ] && ok "$lab README" || bad "$lab README missing"
done

# no stray lab directories
for d in "$ROOT_DIR"/labs/[0-9][0-9]-*/; do
  b=$(basename "$d")
  case " ${expected_labs[*]} " in
    *" $b "*) ;;
    *) bad "unexpected lab directory labs/$b" ;;
  esac
done

printf "\n${B}Lab house style${N}\n"
for lab in "${expected_labs[@]}"; do
  f="$ROOT_DIR/labs/$lab/README.md"
  [ -f "$f" ] || continue
  grep -q "^## Teacher's Playbook" "$f" || bad "$lab README has no Teacher's Playbook"
  grep -qiE "^## (Deliverable|What to keep)|^\*\*Deliverables?\b|the deliverable you keep" \
    "$f" || bad "$lab names no deliverable"
  # every lab except the capstone ships code
  if [ "$lab" != "07-Capstone" ]; then
    ls "$ROOT_DIR/labs/$lab"/*.py >/dev/null 2>&1 || bad "$lab ships no Python"
    [ -f "$ROOT_DIR/labs/$lab/requirements.txt" ] || warn "$lab has no requirements.txt"
  fi
done

# the pipeline contract: labs 02-06 must read ../work
printf "\n${B}Pipeline contract (labs 01-06 chain through work/)${N}\n"
for lab in 02-Search 03-Legal-RAG-Citations 04-Local-Model-Egress-Proof \
           05-Defensible-Review 06-Score-and-Package; do
  if grep -rq -- '\.\./work' "$ROOT_DIR/labs/$lab"/*.py 2>/dev/null; then
    ok "$lab reads ../work"
  else
    bad "$lab does not reference ../work — the Lab NN reads Lab NN-1 chain is broken"
  fi
done

# ------------------------------------------------------------------ course promises
printf "\n${B}Course content checks${N}\n"
grep -qi "Legal AI Engineering" "$ROOT_DIR/README.md" \
  && ok "README names the course" || bad "README does not name the course"
grep -qi "nothing left the building" "$ROOT_DIR/README.md" \
  && ok "README states claim 1 (nothing left the building)" \
  || bad "README does not state claim 1"
grep -qiE "re-run it|reproduc" "$ROOT_DIR/README.md" \
  && ok "README states claim 2 (reproducibility)" || bad "README does not state claim 2"

# the four legal auto-fails must agree across overlay, rubric and code
printf "\n${B}The four legal auto-fails agree across documents${N}\n"
for tag in LEGAL-A LEGAL-B LEGAL-C LEGAL-D; do
  n=0
  for f in course-materials/sais-100-legal-overlay.md course-materials/capstone-rubric.md \
           labs/06-Score-and-Package/sais100.py; do
    grep -q "$tag" "$ROOT_DIR/$f" 2>/dev/null && n=$((n+1))
  done
  [ "$n" = 3 ] && ok "$tag in overlay, rubric and sais100.py" \
    || bad "$tag appears in only $n of 3 (overlay, rubric, sais100.py)"
done

# SAIS-100 is overlaid, not forked
grep -qi "does not fork" "$ROOT_DIR/course-materials/sais-100-legal-overlay.md" \
  && ok "overlay states SAIS-100 is not forked" \
  || bad "overlay must state that it does not fork SAIS-100"

# the model ids in CLAUDE.md are the ones the labs actually default to
printf "\n${B}Model pins${N}\n"
for m in qwen3:8b nomic-embed-text; do
  grep -q "$m" "$ROOT_DIR/labs/common/llm.py" && ok "llm.py defaults to $m" \
    || bad "llm.py does not reference $m"
  grep -q "$m" "$ROOT_DIR/CLAUDE.md" && ok "CLAUDE.md documents $m" \
    || bad "CLAUDE.md does not document $m"
done

# ------------------------------------------------------- no real case data, ever
printf "\n${B}No real case data${N}\n"
if [ -d "$ROOT_DIR/labs/assets/corpus" ]; then
  warn "labs/assets/corpus/ exists locally (generated; must stay gitignored)"
fi
if git -C "$ROOT_DIR" ls-files --error-unmatch labs/assets/corpus >/dev/null 2>&1; then
  bad "labs/assets/corpus is TRACKED IN GIT — generated corpora must never be committed"
else
  ok "no generated corpus tracked in git"
fi
# Directories only. 'labs/*/work*' also matched labs/10-Deploy-At-Scale/work_queue.py,
# which is lab source, not lab output.
tracked_work=$(git -C "$ROOT_DIR" ls-files 'labs/work/*' 'labs/*/work/*' 2>/dev/null | head -1)
[ -z "$tracked_work" ] && ok "no lab work/ output tracked in git" \
  || bad "lab output is tracked in git: $tracked_work"
for pat in 'labs/work' 'assets/corpus'; do
  grep -q "$pat" "$ROOT_DIR/.gitignore" && ok ".gitignore covers $pat" \
    || bad ".gitignore does not cover $pat"
done

# ------------------------------------------------------------------------ summary
printf "\n"
if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
  printf "${G}${B}Course repo structure is valid.${N}\n"
  printf "${D}Next: labs/verify-setup.sh (environment), labs/test-all-labs.sh (labs run).${N}\n"
  exit 0
fi
if [ "$FAIL" -eq 0 ]; then
  printf "${G}${B}Course repo structure is valid${N} ${Y}(%d warning(s)).${N}\n" "$WARN"
  exit 0
fi
printf "${R}${B}%d validation failure(s)${N}" "$FAIL"
[ "$WARN" -gt 0 ] && printf "${Y}, %d warning(s)${N}" "$WARN"
printf ".\n"
exit 1
