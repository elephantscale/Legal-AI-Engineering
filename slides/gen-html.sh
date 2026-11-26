#!/bin/bash
# Generate one self-contained reveal.js HTML deck per source file into html.out/,
# named after the source:
#
#   00-about.html  01-legal-engineer-landscape.html ... 12-governance-deep-dive.html
#
# This is the second release format alongside the PPTX (gen.sh, which Mark runs).
# PDF was dropped on 2026-11-25 — it existed for a webinar that is done. It exists
# because reveal.js gives the instructor three things the PPTX cannot:
#
#   1. Speaker view (press S): the `Notes:` narration from the Markdown, the next
#      slide, a clock and a per-slide timer, in a second window. The deck is
#      scheduled to the minute and Day 2 has no slack, so the timer is the point.
#   2. One file. No PowerPoint, no fonts to install, no network — reveal.js,
#      the stylesheet and every image are inlined. It opens from a USB stick on
#      a client laptop in a room with no wifi, which is the room this course is
#      about.
#   3. A deck a student can keep and actually read afterwards, with working
#      links, searchable text (Ctrl+Shift+F) and per-slide anchors (#/13).
#
# The Markdown stays the source of truth. The only transformation is
# md2reveal.py turning house-style `Notes:` blocks into reveal.js speaker notes;
# slides are split on the `---` separators already in the source, via pandoc
# --slide-level=0. No deck is restructured to suit this build.
#
# Usage:
#   ./gen-html.sh                  build every deck into html.out/
#   ./gen-html.sh 01 06            build only the decks whose names start 01, 06
#   ./gen-html.sh --release        build every deck, then copy into release/
#   ./gen-html.sh --fetch-reveal   re-vendor revealjs/ from upstream (needs network)
#
# Requires pandoc (3.0+, for --embed-resources). Everything else is in the repo.

set -euo pipefail
cd "$(dirname "$0")"

REVEAL_DIR="revealjs"
REVEAL_VERSION="5.1.0"
OUT="html.out"
THEME="${REVEAL_THEME:-white}"          # any file in revealjs/dist/theme/
RELEASE_DIR="release"

# The exact set of files pandoc's revealjs template references. notes, search
# and zoom are loaded unconditionally by the template, so all three must exist
# or Reveal.initialize() dies on a missing global.
REVEAL_FILES=(
    dist/reset.css
    dist/reveal.css
    dist/reveal.js
    plugin/notes/notes.js
    plugin/search/search.js
    plugin/zoom/zoom.js
)

# ---------------------------------------------------------------- re-vendoring

fetch_reveal() {
    local url="https://github.com/hakimel/reveal.js/archive/refs/tags/${REVEAL_VERSION}.tar.gz"
    local tmp
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' RETURN

    echo "Fetching reveal.js ${REVEAL_VERSION} ..."
    curl -fsSL -o "$tmp/reveal.tar.gz" "$url"
    tar -xzf "$tmp/reveal.tar.gz" -C "$tmp"
    local src="$tmp/reveal.js-${REVEAL_VERSION}"

    rm -rf "$REVEAL_DIR"
    for f in "${REVEAL_FILES[@]}"; do
        mkdir -p "$REVEAL_DIR/$(dirname "$f")"
        cp "$src/$f" "$REVEAL_DIR/$f"
    done
    mkdir -p "$REVEAL_DIR/dist/theme"
    cp "$src"/dist/theme/*.css "$REVEAL_DIR/dist/theme/"
    # Strip every webfont @import from the themes. Two reasons, and the second
    # one is not cosmetic:
    #   - reveal-theme.css sets the font stack to the system sans deliberately,
    #     so a bundled font (Source Sans Pro) would be downloaded, inlined into
    #     every deck, and never used.
    #   - half the themes @import fonts.googleapis.com. A deck for a course
    #     that teaches an enforced egress boundary must not call out to Google
    #     to render its own slides, in the room or at build time.
    sed -i '/@import url(/d' "$REVEAL_DIR"/dist/theme/*.css
    cp "$src/LICENSE" "$REVEAL_DIR/LICENSE"
    cat > "$REVEAL_DIR/VERSION" <<EOF
reveal.js ${REVEAL_VERSION} — https://github.com/hakimel/reveal.js (MIT, see LICENSE)

Vendored, not fetched at build time: a deck must be buildable on a plane, and a
course that teaches an enforced egress boundary should not phone a CDN to render
its own slides. Trimmed to the files pandoc's revealjs template references, plus
all themes. Re-vendor with ./gen-html.sh --fetch-reveal.
EOF
    echo "Vendored into $REVEAL_DIR/ ($(du -sh "$REVEAL_DIR" | cut -f1))"
}

# ------------------------------------------------------------------- arguments

do_release=0
patterns=()
for arg in "$@"; do
    case "$arg" in
        --fetch-reveal) fetch_reveal; exit 0 ;;
        --release)      do_release=1 ;;
        -h|--help)      sed -n '2,30p' "$0"; exit 0 ;;
        -*)             echo "unknown option: $arg" >&2; exit 2 ;;
        *)              patterns+=("$arg") ;;
    esac
done

# --------------------------------------------------------------------- checks

command -v pandoc >/dev/null || { echo "pandoc not found — install pandoc 3.0+" >&2; exit 1; }

missing=0
for f in "${REVEAL_FILES[@]}"; do
    [ -f "$REVEAL_DIR/$f" ] || { echo "missing $REVEAL_DIR/$f" >&2; missing=1; }
done
[ -f "$REVEAL_DIR/dist/theme/$THEME.css" ] || {
    echo "theme '$THEME' not in $REVEAL_DIR/dist/theme/" >&2; missing=1; }
if [ "$missing" = 1 ]; then
    echo "Run ./gen-html.sh --fetch-reveal to re-vendor reveal.js." >&2
    exit 1
fi

# 0. Refresh the manifest from what is actually on disk, the same way gen.sh does.
ls [0-9][0-9]-*.md | sort > slide-list.txt

# Which decks?
decks=()
if [ "${#patterns[@]}" -eq 0 ]; then
    while IFS= read -r line; do decks+=("$line"); done < slide-list.txt
else
    for p in "${patterns[@]}"; do
        found=0
        for d in $(cat slide-list.txt); do
            case "$d" in "$p"*) decks+=("$d"); found=1 ;; esac
        done
        [ "$found" = 1 ] || { echo "no deck matches '$p'" >&2; exit 1; }
    done
fi

mkdir -p "$OUT"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# ---------------------------------------------------------------------- build

for src in "${decks[@]}"; do
    base="${src%.md}"
    pre="$scratch/$base.pre.md"

    # House-style `Notes:` blocks -> pandoc notes divs -> <aside class="notes">.
    python3 md2reveal.py "$src" > "$pre"

    # The deck carries its own title slide, so set only the browser tab title:
    # giving pandoc `title` metadata would make it generate a second one.
    tab_title="$(sed -n '1s/^#\+[[:space:]]*//p' "$src")"
    [ -n "$tab_title" ] || tab_title="$base"

    pandoc \
        --from=markdown \
        --to=revealjs \
        --standalone \
        --embed-resources \
        --slide-level=0 \
        --metadata pagetitle="$tab_title" \
        --variable revealjs-url="$REVEAL_DIR" \
        --variable theme="$THEME" \
        --variable css="reveal-theme.css" \
        --variable width=1280 \
        --variable height=800 \
        --variable margin=0.045 \
        --variable minScale=0.2 \
        --variable maxScale=2.0 \
        --variable center=false \
        --variable controls=true \
        --variable progress=true \
        --variable slideNumber="'c/t'" \
        --variable hash=true \
        --variable transition=none \
        --variable backgroundTransition=none \
        --output "$OUT/$base.html" \
        "$pre"

    slides=$(grep -o '<section' "$OUT/$base.html" | wc -l)
    notes=$(grep -o 'class="notes"' "$OUT/$base.html" | wc -l)
    printf '  %-42s %3s slides  %3s with notes  %6s\n' \
        "$base.html" "$slides" "$notes" "$(du -h "$OUT/$base.html" | cut -f1)"
done

echo "Done. Decks in $(pwd)/$OUT:"
ls -1 "$OUT"/*.html | sed 's#^#  #'

if [ "$do_release" = 1 ]; then
    mkdir -p "$RELEASE_DIR"
    for src in "${decks[@]}"; do
        cp -f "$OUT/${src%.md}.html" "$RELEASE_DIR/"
    done
    echo "Copied into $RELEASE_DIR/."
fi

cat <<'EOF'

In the room:
  S                 speaker view — narration, next slide, clock, per-slide timer
  Esc / O           slide overview
  F                 full screen
  Ctrl+Shift+F      search the deck
  ?                 all shortcuts
  append ?print-pdf then print to PDF for a paper copy
EOF
