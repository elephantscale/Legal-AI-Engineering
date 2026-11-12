#!/bin/bash
# Generate one pptx per source file into assembly.out/, named after the source:
#
#   00-about.pptx  01-legal-engineer-landscape.pptx ... 12-governance-deep-dive.pptx
#
# The shared assembler ($ES_HOME/utils/presentations/slides-assembler.sh) prefixes
# its output with a 1-based counter (01__00-about.pptx, 02__01-..., ...). Our source
# filenames already carry the module number, so the counter is redundant and off by
# one. We leave that shared tool untouched and strip the prefix here, the same way
# Building-Agentic-AI/slides/gen.sh does. The names still sort in teaching order
# because the module number is the first thing in them.
set -euo pipefail
cd "$(dirname "$0")"

# 0. Refresh the manifest from what is actually on disk.
ls [0-9][0-9]-*.md | sort > slide-list.txt

# 1. Build all decks with the shared assembler (produces 01__*, 02__*, ...).
"$ES_HOME"/utils/presentations/slides-assembler.sh slide-list.txt

# 2. Strip the assembler's NN__ counter prefix.
cd assembly.out
for f in [0-9][0-9]__*; do
    [ -e "$f" ] || continue            # no matches -> skip
    mv -f -- "$f" "${f#*__}"
done

echo "Done. Decks in $(pwd):"
ls -1 [0-9][0-9]-*.pptx
