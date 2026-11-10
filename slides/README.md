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

## Conventions

- Every content deck opens with a title slide (`# Title` + `Elephant Scale`) and ends with a
  lab hand-off slide.
- `>` blockquotes are the visual beat / key takeaway for the slide — one per slide, maximum.
- `Notes:` blocks are **instructor narration**, not student content.
- Images: `<img src="../images/foo.png" style="width:60%;"/>` — `src` + `width` only; final
  layout lives in the PPTX.
