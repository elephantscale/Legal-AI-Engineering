# Slides

Source markdown for the decks, one file per module plus `00-about.md`.
**The Markdown is the source of truth.**

| Deck | Module | Day |
|---|---|---|
| `00-about.md` | Course intro, agenda, ground rules | — |
| `01-legal-engineer-landscape.md` | 1 — The Legal Engineer's Landscape | 1 |
| `02-legal-data-ingestion.md` | 2 — Legal Data Is Messy | 1 |
| `03-search-and-retrieval.md` | 3 — Search and Retrieval | 1 |
| `04-legal-rag-citations.md` | 4 — RAG With Citations | 1 |
| `05-privilege-and-local-serving.md` | 5 — Privacy, Privilege, Local Serving | 2 |
| `06-defensible-review.md` | 6 — Defensible AI Review | 2 |
| `07-ship-score-govern.md` | 7 — Ship It: Workflow, Deployment, Governance | 2 |
| `08-capstone.md` | Capstone + close | 2 |
| `09-investigations.md` | 9 — Investigations | 3 (optional) |
| `10-agentic-legal-workflows.md` | 10 — Agentic Legal Workflows | 3 (optional) |
| `11-deployment-at-scale.md` | 11 — Deployment at Scale | 3 (optional) |
| `12-governance-deep-dive.md` | 12 — Governance Deep-Dive | 3 (optional) |

Build with:

```sh
./gen.sh
```

This refreshes `slide-list.txt`, calls the shared assembler
(`$ES_HOME/utils/presentations/slides-assembler.sh`) and renumbers the output 0-based into
`assembly.out/`:

```
00__00-about.pptx  01__01-legal-engineer-landscape.pptx  ...  12__12-governance-deep-dive.pptx
```

`assembly.out/` is gitignored. Copy the decks you deliver into `slides/release/`.

## reveal.js (HTML)

The second release format alongside the PPTX, built from the same Markdown. (PDF was
dropped as a release format on 2026-11-25 — it existed for a webinar that is done. You can
still print one on demand; see `?print-pdf` below.)

```sh
./gen-html.sh                  # every deck -> html.out/
./gen-html.sh 01 06            # just those decks
./gen-html.sh --release        # build, then copy into release/
./gen-html.sh --fetch-reveal   # re-vendor revealjs/ from upstream (needs network)
```

Needs `pandoc` 3.0+. Nothing else: reveal.js is vendored in `revealjs/` (MIT, 5.1.0,
~400 KB, webfont `@import`s stripped), so a deck builds on a plane. `html.out/` is
gitignored; `release/` is committed.

**Each deck is one self-contained HTML file.** reveal.js, `reveal-theme.css` and every
image are inlined, so it opens from a USB stick on a client laptop with no network, no
PowerPoint and no fonts to install — which is the room this course is about. The only
things it reaches for are the citation hyperlinks in the slide text, and only if clicked.

What it gives the instructor that the PPTX does not:

| Key | |
|---|---|
| `S` | **Speaker view** — the `Notes:` narration, the next slide, a clock and a per-slide timer, in a second window. Day 2 has no slack; the timer is the point. |
| `Esc` / `O` | Slide overview — jump anywhere when a question skips ahead |
| `Ctrl+Shift+F` | Search the deck |
| `F` | Full screen |
| `?` | All shortcuts |

Append `?print-pdf` to the URL and print to get a PDF without going through PowerPoint.
Per-slide anchors (`#/13`) work, so you can link someone to one slide.

### Opening a deck — `./present.sh`

A deck is a web page, so the browser is the tool; there is nothing better to open it with.
Don't double-click it in the IDE — that loads 2.7 MB of generated HTML into the editor. In
JetBrains use **Alt+F2** (or right-click → *Open In → Browser*). Otherwise:

```sh
./present.sh 01            # Module 1, newest build, in a chromeless window
./present.sh capstone      # match on name instead of number
./present.sh --list        # what is built, and whether it is current
./present.sh 01 --pdf      # open with ?print-pdf, then Ctrl+P -> Save as PDF
./present.sh 01 --url      # just print the file:// URL
./present.sh 01 --release  # force the committed release/ copy
```

It opens Chrome in **app mode** — no tab strip, address bar or bookmarks across the top of
your slides — and prefers `html.out/` over `release/`. Two things it does that opening the
file by hand does not:

- **It refuses to let you present a stale deck quietly.** If the `.md` is newer than the
  built `.html`, it says so and names the rebuild command. `--list` shows this for every deck
  at once, which is the check worth running the morning of a delivery.
- **It tells you the keys** — and that if speaker view does not appear, Chrome blocked the
  popup. Allow popups for the deck *before* you present, not during.

No server is needed: speaker view, the timer and the `?receiver` windows all work from
`file://` (verified — `location.origin` is `file://` and Chrome honours the query string), so
the USB-stick-on-a-client-laptop case holds.

### How it maps to the Markdown

- **Slides split on the `---` separators already in the source** (`pandoc --slide-level=0`).
  Headings, tables, blockquotes and code blocks pass through untouched. No deck is
  restructured to suit this build.
- **`Notes:` blocks become speaker notes.** `md2reveal.py` rewrites them into pandoc
  `::::: notes` divs, which become `<aside class="notes">` — read by the speaker view,
  never shown on the projector. Same contract as the PPTX notes pane.
- **`>` blockquotes render as the slide's takeaway callout**, because that is what house
  style already uses them for. A slide missing its visual beat is now obvious at a glance.
- Colours and type scale are variables at the top of `reveal-theme.css`. Pick another
  reveal theme with `REVEAL_THEME=solarized ./gen-html.sh`.
- A slide that overruns the canvas scrolls rather than cropping. If you are scrolling in
  the room, the slide is too long — useful signal during a timed run-through.

## Conventions

- Every content deck opens with a title slide (`# Title` + `Elephant Scale`) and ends with a
  lab hand-off slide.
- `>` blockquotes are the visual beat / key takeaway for the slide — one per slide, maximum.
- `Notes:` blocks are **instructor narration**, not student content.
- Images: `<img src="../images/foo.png" style="width:60%;"/>` — `src` + `width` only; final
  layout lives in the PPTX.
