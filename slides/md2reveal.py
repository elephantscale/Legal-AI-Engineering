#!/usr/bin/env python3
"""Prepare a slide deck's Markdown for pandoc's reveal.js writer.

The decks in this directory are the source of truth and this script does not
restructure them. It makes exactly one change: an instructor-narration block,
written in house style as a bare

    Notes:

    ...prose until the next slide separator...

becomes a pandoc fenced div

    ::::: notes
    ...
    :::::

which pandoc's revealjs writer emits as <aside class="notes"> -- the markup
reveal.js's speaker view (press S) reads. Narration therefore lands in the
presenter window and never on the projector, the same contract the PPTX build
honours by putting it in the notes pane.

Everything else is left byte-for-byte alone. Slides are split by pandoc on the
'---' separators already in the source (pandoc --slide-level=0), so headings,
tables, blockquotes and code blocks pass through untouched.

Fence-aware: a 'Notes:' line, a '---' separator or a '#' heading inside a
``` or ~~~ code block is content, not markup. Several decks have shell
comments that start a line with '#', and those must survive verbatim.

Usage:  md2reveal.py INPUT.md > OUTPUT.md
"""

import re
import sys

FENCE = re.compile(r"^\s*(?:```|~~~)")
NOTES = re.compile(r"^Notes:\s*$")
SEPARATOR = re.compile(r"^---\s*$")
# Five colons, so a fenced div inside the narration could not close ours early.
OPEN, CLOSE = "::::: notes", ":::::"


def convert(lines):
    out = []
    in_fence = False       # inside a ``` / ~~~ code block
    in_notes = False       # inside a Notes: block we are wrapping
    pending = []           # narration lines held back, so we can trim trailing blanks

    def flush_notes():
        """Close the open notes div, trimming blank lines at both ends."""
        nonlocal in_notes
        while pending and not pending[0].strip():
            pending.pop(0)
        while pending and not pending[-1].strip():
            pending.pop()
        out.extend(pending)
        out.append("")
        out.append(CLOSE)
        out.append("")
        pending.clear()
        in_notes = False

    for line in lines:
        line = line.rstrip("\n")

        if FENCE.match(line):
            in_fence = not in_fence
            (pending if in_notes else out).append(line)
            continue

        if in_fence:
            (pending if in_notes else out).append(line)
            continue

        if in_notes:
            # A separator ends the slide, and with it the narration.
            if SEPARATOR.match(line):
                flush_notes()
                out.append(line)
            else:
                pending.append(line)
            continue

        if NOTES.match(line):
            in_notes = True
            out.append(OPEN)
            out.append("")
            continue

        out.append(line)

    if in_notes:
        flush_notes()
    if in_fence:
        print("md2reveal: warning: unclosed code fence in input", file=sys.stderr)
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    with open(sys.argv[1], encoding="utf-8") as fh:
        lines = fh.readlines()
    sys.stdout.write("\n".join(convert(lines)) + "\n")


if __name__ == "__main__":
    main()
