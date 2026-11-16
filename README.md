# Legal AI Engineering

*Building private, defensible AI for law — eDiscovery, review, and investigations.*

### Table of Contents

- [Course Outline](outline.md)
- [Slides](slides/)
- [Labs](labs/)
- [Course Materials](course-materials/) — rubrics, checklists, templates students keep
- [Lab Setup](labs/SETUP.md) — Python 3.10+ is the only hard requirement

---

The legal-vertical track of the Elephant Scale Secure AI Learning Path. Two intensive,
hands-on days that turn a software or AI engineer into a **legal engineer** — someone who
can actually build AI for legal work and then defend it.

The through-line is two risks that never go away: **confidentiality/privilege** (where did
the document go?) and **defensibility** (can you prove what the system did?). They come down
to two sentences a student must be able to say in front of a court, a client, or a regulator:

> 1. **"Nothing left the building."**
> 2. **"Here is exactly what the system did, and you can re-run it."**

Every module serves one of those two, and every lab produces the artifact that proves it — an
egress attestation, a citation trail, a recall measurement, a reproducibility bundle. If a
slide or a lab does not serve one of them, it is not in the course.

The labs compound. By the end of Day 2 you have one working system: a messy corpus
ingested, indexed, searchable, answerable with citations from a **local** model that
provably never phoned home, measured against a blind ground truth, scored with
**SAIS-100**, and packaged for on-prem deployment.

**FreeEed** — the Apache-2.0, on-prem eDiscovery platform the instructor ships — is the
reference architecture throughout: Tika extraction across 1,400+ file types, OCR, imaging,
PST/OST, Solr/Lucene search, review, and Bates/load-file production. The labs are
self-contained Python over a synthetic corpus, designed against that architecture, so what
you build here transfers to a system you can actually deploy.

Two products: a **2-day Core** (the build path, and the certificate bar) and a **1-day Deep Dive**
scheduled separately (ship it, oversee it, prove it), plus **electives** — investigations and
deployment at scale. They can still run as three consecutive days on request. See
[`outline.md`](outline.md) for the full description, audience, learning outcomes, modules, and the
module ↔ lab map.
