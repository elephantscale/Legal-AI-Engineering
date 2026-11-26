#!/bin/bash
# Open a reveal.js deck in a chromeless browser window, ready to present.
#
#   ./present.sh 01            Module 1, newest build
#   ./present.sh 1             same — one digit is fine
#   ./present.sh capstone      match on name instead of number
#   ./present.sh about         the 00-about deck
#   ./present.sh --list        what is built, and whether it is current
#   ./present.sh 01 --pdf      open with ?print-pdf, then Ctrl+P -> Save as PDF
#   ./present.sh 01 --url      just print the file:// URL, open nothing
#   ./present.sh 01 --release  force the committed release/ copy
#
# Why this exists: double-clicking a deck in the IDE opens 2.7 MB of generated
# HTML in the editor, and `xdg-open` gives you a browser window with tabs, an
# address bar and bookmarks across the top of your slides. Chrome's app mode
# gives a clean window instead.
#
# It prefers html.out/ (your latest build) over release/ (the committed copy),
# and it REFUSES TO STAY QUIET if the deck is older than the Markdown it was
# built from — presenting a stale deck is the failure this script exists to
# prevent. The Markdown is the source of truth; this only ever reads it.
#
# In the room:
#   S              speaker view — narration, next slide, clock, per-slide timer
#   F              full screen            Esc / O   slide overview
#   Ctrl+Shift+F   search the deck        ?         all shortcuts
#
# If speaker view does not appear, Chrome blocked the popup: allow popups for
# this deck BEFORE you present, not during.

set -euo pipefail
cd "$(dirname "$0")"

BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; YEL=$'\033[33m'; GRN=$'\033[32m'; N=$'\033[0m'

die() { printf '%s%s%s\n' "$RED" "$*" "$N" >&2; exit 1; }

# ------------------------------------------------------------------ arguments
want=""; use_release=0; as_pdf=0; url_only=0; do_list=0

for arg in "$@"; do
    case "$arg" in
        --list|-l)    do_list=1 ;;
        --release|-r) use_release=1 ;;
        --pdf|-p)     as_pdf=1 ;;
        --url|-u)     url_only=1 ;;
        --help|-h)    sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*)           die "unknown option: $arg  (try --help)" ;;
        *)            [ -n "$want" ] && die "give one deck, not two: '$want' and '$arg'"
                      want="$arg" ;;
    esac
done

sources=( [0-9][0-9]-*.md )
[ -e "${sources[0]}" ] || die "no decks here — run this from the slides/ directory"

# newest built copy of a deck, honouring --release
built_copy() {
    local base="$1" c
    if [ "$use_release" = 1 ]; then
        [ -f "release/$base.html" ] && { printf 'release/%s.html' "$base"; return 0; }
        return 1
    fi
    for c in "html.out/$base.html" "release/$base.html"; do
        [ -f "$c" ] && { printf '%s' "$c"; return 0; }
    done
    return 1
}

# ----------------------------------------------------------------------- list
if [ "$do_list" = 1 ] || [ -z "$want" ]; then
    [ -z "$want" ] && [ "$do_list" = 0 ] && printf '%sName a deck.%s  Built decks:\n\n' "$BOLD" "$N"
    [ "$do_list" = 1 ] && printf '%sDecks%s\n\n' "$BOLD" "$N"
    for src in "${sources[@]}"; do
        base="${src%.md}"
        if deck="$(built_copy "$base")"; then
            if [ "$src" -nt "$deck" ]; then
                state="${YEL}stale — rebuild${N}"
            else
                state="${GRN}current${N}"
            fi
            printf '  %-38s %-10s %s%s%s\n' "$base" "$state" "$DIM" "$deck" "$N"
        else
            printf '  %-38s %snot built%s\n' "$base" "$DIM" "$N"
        fi
    done
    printf '\n%sBuild with ./gen-html.sh [NN ...], present with ./present.sh NN%s\n' "$DIM" "$N"
    exit 0
fi

# -------------------------------------------------------------------- resolve
# a bare number means the module number; anything else matches the name
if [[ "$want" =~ ^[0-9]{1,2}$ ]]; then
    pattern="$(printf '%02d' "$((10#$want))")-*"
else
    pattern="*${want}*"
fi

matches=()
for src in "${sources[@]}"; do
    base="${src%.md}"
    # shellcheck disable=SC2053
    [[ "$base" == $pattern ]] && matches+=( "$base" )
done

if [ "${#matches[@]}" -eq 0 ]; then
    die "no deck matches '$want' — ./present.sh --list to see them"
elif [ "${#matches[@]}" -gt 1 ]; then
    printf '%s'"'"'%s'"'"' matches %d decks:%s\n' "$RED" "$want" "${#matches[@]}" "$N" >&2
    printf '  %s\n' "${matches[@]}" >&2
    exit 1
fi

base="${matches[0]}"
deck="$(built_copy "$base")" || die "$base is not built$([ "$use_release" = 1 ] && echo ' in release/') — run ./gen-html.sh ${base%%-*}"

# ------------------------------------------------------- stale-deck guardrail
if [ "$base.md" -nt "$deck" ]; then
    printf '%s⚠  %s is OLDER than %s.md%s\n' "$YEL" "$deck" "$base" "$N" >&2
    printf '   You are about to present a deck that predates its source.\n' >&2
    printf '   Rebuild:  ./gen-html.sh %s\n\n' "${base%%-*}" >&2
fi

url="file://$(realpath "$deck")"
[ "$as_pdf" = 1 ] && url="$url?print-pdf"

if [ "$url_only" = 1 ]; then
    printf '%s\n' "$url"
    exit 0
fi

# --------------------------------------------------------------------- launch
browser=""
for b in google-chrome google-chrome-stable chromium chromium-browser; do
    command -v "$b" >/dev/null 2>&1 && { browser="$b"; break; }
done

printf '%s%s%s  %s%s%s\n' "$BOLD" "$base" "$N" "$DIM" "$deck" "$N"

if [ -n "$browser" ]; then
    # app mode: no tab strip, no address bar, no bookmarks over your slides
    nohup "$browser" --new-window --app="$url" >/dev/null 2>&1 &
    disown
    if [ "$as_pdf" = 1 ]; then
        printf '%sPrint to PDF: Ctrl+P, Destination "Save as PDF", Margins None, Background graphics ON%s\n' "$DIM" "$N"
    else
        printf '%sF full screen · S speaker view + timer · Esc overview · ? shortcuts%s\n' "$DIM" "$N"
    fi
else
    printf '%sNo Chrome/Chromium found — falling back to your default browser (expect tabs and an address bar).%s\n' "$YEL" "$N"
    xdg-open "$url" >/dev/null 2>&1 &
    disown
fi
