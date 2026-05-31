# AI-University — Enterprise AI Knowledge Publishing Platform

A complete, automated **AI learning publishing system** that generates, stores,
indexes, searches, views and downloads professional, enterprise-grade AI books.

The platform ships three things:

1. **A content-generation engine** (`engine/`) that procedurally authors
   substantive, professionally structured AI books — every one with the full
   21-part front/back matter, 20–30 chapters, professional diagrams, runnable
   code, case studies, labs and assessments.
2. **A multi-format publishing pipeline** that exports each book to
   **Markdown, HTML, PDF, DOCX and a 30+ slide PPTX** deck, and stores every
   diagram's source separately (Mermaid, PlantUML, SVG, Draw.io XML).
3. **A web portal** (`web/`) — a complete library, document viewer, PDF/format
   download centre, full-text search, filters, diagram browser, bookmarks,
   favourites, reading-progress tracking, learning paths and certification
   paths.

---

## Targets vs. achieved

The engine is configured to generate **528 books across 33 AI categories**
(16 per category). Running `aupub catalog` builds the full catalog and reports
aggregate metrics:

| Metric | Target | Achieved (528-book catalog) |
| --- | ---: | ---: |
| Books | 500+ | **528** |
| Pages | 125,000+ | **146,474** |
| Words | 10,000,000+ | **33,629,999** |
| Diagrams | 10,000+ | **17,853** |
| Code samples | 5,000+ | **12,672** |
| Assessment/interview questions | 10,000+ | **52,800** |
| Categories | — | **33** |
| Chapters | — | **13,200** |

Each individual book is a **250+ page** professional document. The rendered PDFs
in the committed demo measure **254–263 physical A4 pages**.

> **What is committed vs. generated on demand.** Materialising the full
> 33M-word corpus (every PDF/DOCX/PPTX for all 528 books) is several gigabytes,
> which is impractical to commit to git. This repository therefore commits:
>
> - the **complete catalog** of all 528 books (lightweight `data/library.json`
>   plus a per-book outline in `data/outlines/`, a `data/search-index.json`, and
>   `data/stats.json`), so the portal can browse, search and preview **every**
>   title; and
> - a **fully-exported demo corpus** of 12 books (one from each of the first 12
>   categories) in `content/`, with all five formats, diagram sources and
>   structured content.
>
> Any book — or the entire catalog — can be fully published on demand with a
> single command (see below).

---

## Repository layout

```
.
├── engine/                     # The publishing engine (Python)
│   └── aupub/
│       ├── knowledge/          # Structured domain knowledge (33 categories)
│       ├── generators/         # prose, diagrams, code, quiz, book assembly
│       ├── exporters/          # markdown, html, pdf, docx, pptx, diagram files
│       ├── catalog.py          # 500+ book catalog definitions
│       ├── publish.py          # publishing orchestration
│       └── cli.py              # `python -m aupub.cli ...`
├── web/                        # The portal (framework-free SPA)
│   ├── index.html, styles.css, app.js
├── data/                       # Generated catalog, outlines, search index, stats
├── content/                    # Generated, fully-exported demo corpus (12 books)
├── serve.py                    # Static server for the portal + artefacts
└── README.md
```

---

## Quick start

### 1. Install engine dependencies

```bash
cd engine
python -m pip install -r requirements.txt
```

### 2. Build the full catalog (528 books, ~3 seconds)

```bash
cd engine
python -m aupub.cli catalog
```

This writes `data/library.json`, `data/outlines/*.json`,
`data/categories.json`, `data/search-index.json` and `data/stats.json`.

### 3. Publish books to all formats

```bash
cd engine
# one book from each of the first 12 categories (the committed demo)
python -m aupub.cli publish --demo 12

# everything in a category
python -m aupub.cli publish --category rag

# specific titles
python -m aupub.cli publish --ids AIU-0001,AIU-0113

# the entire catalog (large — many GB)
python -m aupub.cli publish
```

Each published book lands in `content/<category>/<slug>/` with
`<slug>.md`, `.html`, `.pdf`, `.docx`, `.pptx`, a `diagrams/` folder of source
files, `content.json` (for the in-app viewer) and `manifest.json`.

### 4. Launch the portal

```bash
# from the repository root
python serve.py
# open http://localhost:8000/web/
```

---

## The portal

Open `http://localhost:8000/web/` after running `serve.py`. Features:

- **Dashboard** — live metrics vs. targets, category overview, continue-reading.
- **Document Library** — all 528 books with category/level/format filters,
  sorting, search and pagination.
- **Categories** — browse the 33 subject areas.
- **Document & PDF Viewer** — read any published book online with fully
  rendered, self-contained SVG diagrams (no external renderer / works offline),
  syntax-highlighted code, inline assessments and a sticky table of contents;
  non-published titles show a full outline preview.
- **Search** — instant full-text search across titles, chapters and topics.
- **Diagram Browser** — explore the 20 diagram types and four source formats.
- **Download Center** — download PDF, DOCX, PPTX, HTML and Markdown.
- **Learning Paths & Certification Paths** — curated multi-book tracks.
- **Bookmarks, Favorites & Reading Progress** — persisted locally.
- **Light/dark theme**.

---

## How content is generated

Content is **not** lorem-ipsum filler. The engine composes each chapter from a
curated domain knowledge base (`engine/aupub/knowledge/domains.py`) that
encodes, for all 33 categories, real definitions, architecture, design
patterns, best practices, pitfalls, industry use cases, tooling, glossaries and
authoritative references. The prose composer weaves these into varied,
technically substantive sections — theory, architecture, deep dives, worked
examples, governance/security/cost notes, exercises and takeaways — anchored to
the specific concept of each chapter.

Every book includes all 21 required document sections (cover, copyright, table
of contents, list of figures, list of tables, executive summary, learning
objectives, the five enterprise perspectives, hands-on labs, case studies,
interview/certification/assessment questions, references, glossary and index),
plus 20–30 chapters of body content with 20+ professional diagrams.

Generation is **deterministic** (seeded per book), so the catalog and content
are fully reproducible.

---

## Diagram formats

Diagrams are generated in four professional formats and stored as separate
source files alongside each published book:

- **Mermaid** (`.mmd`) — flowcharts, sequence, class, knowledge-graph diagrams
- **PlantUML** (`.puml`) — component, deployment, sequence diagrams
- **SVG** (`.svg`) — rendered capability/architecture maps
- **Draw.io XML** (`.drawio`) — editable architecture diagrams

In addition to the editable source above, every diagram is also rendered to a
**self-contained SVG** that the web viewer and the HTML export embed inline, so
diagrams are always visible without any external renderer or internet access.
(The PDF and DOCX exports include the editable diagram source.)

Diagram types include architecture, application flow, business process, data
flow, sequence, class, component, deployment, network, cloud architecture, RAG
architecture, agent architecture, security architecture, DevOps/CI-CD pipelines,
infrastructure, knowledge graph, data lineage, capability maps and operating
models.

---

## Categories (33)

AI Foundations · Generative AI · Prompt Engineering · LLMs · Transformers ·
Embeddings · Vector Databases · RAG · GraphRAG · Knowledge Graphs · Agentic AI ·
Multi-Agent Systems · MCP · Cursor IDE · Claude · OpenAI · Gemini · Anthropic ·
Fine Tuning · LoRA · PEFT · RLHF · AI Security · Responsible AI · AI Governance ·
LLMOps · MLOps · AIOps · AgentOps · AI Architecture · AI Testing ·
AI Observability · AI Product Management.

---

## Scaling to the full corpus

To regenerate the full catalog and publish **all** books in every format:

```bash
cd engine
python -m aupub.cli --per-category 16 catalog
python -m aupub.cli --per-category 16 publish      # warning: many GB
```

Increase `--per-category` to grow the library further (e.g. `--per-category 20`
yields 660 books). The engine streams output per book, so generation scales
linearly and can be resumed by category or id.
