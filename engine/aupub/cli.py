"""Command-line interface for the AI-University publishing engine.

Commands
--------
catalog   Build the full catalog of 500+ books: a lightweight library index,
          per-book outlines, category rollups, aggregate stats and a search
          index -- without materialising heavy artefacts.
publish   Fully publish a selection of books to Markdown, HTML, PDF, DOCX and
          PPTX (plus diagram sources and structured content) into ``content/``.
stats     Print aggregate statistics for the configured catalog.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from .catalog import build_specs
from .generators.book import build_book
from .knowledge import CATEGORIES
from .publish import build_search_record, publish_book

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT, "data")
CONTENT_DIR = os.path.join(ROOT, "content")


def _book_outline(book) -> dict:
    entry = book.catalog_entry()
    entry["chapters"] = [
        {
            "number": c.number,
            "title": c.title,
            "summary": c.summary,
            "estimated_pages": c.estimated_pages,
            "sections": [s.heading for s in c.sections],
            "diagrams": [{"title": d.title, "kind": d.kind, "fmt": d.fmt}
                         for d in c.diagrams],
        }
        for c in book.chapters
    ]
    return entry


def cmd_catalog(args: argparse.Namespace) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    outlines_dir = os.path.join(DATA_DIR, "outlines")
    os.makedirs(outlines_dir, exist_ok=True)
    specs = build_specs(per_category=args.per_category)
    print(f"Building catalog for {len(specs)} books...", file=sys.stderr)
    library: list[dict] = []
    search: list[dict] = []
    totals = {"books": 0, "pages": 0, "words": 0, "diagrams": 0, "code": 0,
              "questions": 0, "chapters": 0}
    cat_counts: dict[str, dict] = {}
    t0 = time.time()
    for i, spec in enumerate(specs, 1):
        book = build_book(spec)
        library.append(book.catalog_entry())
        with open(os.path.join(outlines_dir, f"{book.id}.json"), "w", encoding="utf-8") as fh:
            json.dump(_book_outline(book), fh, ensure_ascii=False)
        search.append(build_search_record(book, os.path.join(book.category_slug, book.slug)))
        totals["books"] += 1
        totals["pages"] += book.estimated_pages
        totals["words"] += book.word_count
        totals["diagrams"] += book.diagram_count
        totals["code"] += book.code_count
        totals["questions"] += book.question_count
        totals["chapters"] += book.chapter_count
        c = cat_counts.setdefault(book.category_slug, {
            "name": book.category, "slug": book.category_slug, "books": 0,
            "pages": 0, "words": 0, "diagrams": 0})
        c["books"] += 1
        c["pages"] += book.estimated_pages
        c["words"] += book.word_count
        c["diagrams"] += book.diagram_count
        if i % 100 == 0:
            print(f"  ... {i}/{len(specs)} ({time.time()-t0:.1f}s)", file=sys.stderr)

    categories = []
    for c in CATEGORIES:
        info = cat_counts.get(c["slug"], {"books": 0, "pages": 0, "words": 0, "diagrams": 0})
        categories.append({
            "name": c["name"], "slug": c["slug"], "tagline": c["tagline"],
            "books": info["books"], "pages": info["pages"], "words": info["words"],
            "diagrams": info["diagrams"],
        })

    with open(os.path.join(DATA_DIR, "library.json"), "w", encoding="utf-8") as fh:
        json.dump(library, fh, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "categories.json"), "w", encoding="utf-8") as fh:
        json.dump(categories, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA_DIR, "search-index.json"), "w", encoding="utf-8") as fh:
        json.dump(search, fh, ensure_ascii=False)

    stats = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories": len(categories),
        **totals,
        "targets": {
            "books": 500, "pages": 125000, "words": 10_000_000,
            "diagrams": 10000, "code": 5000, "questions": 10000,
        },
    }
    with open(os.path.join(DATA_DIR, "stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)

    print(json.dumps(stats, indent=2))
    print(f"Catalog written to {DATA_DIR} in {time.time()-t0:.1f}s", file=sys.stderr)


def _select_specs(specs, args):
    if args.ids:
        wanted = set(args.ids.split(","))
        return [s for s in specs if s.id in wanted]
    pool = specs
    if args.category:
        pool = [s for s in pool if s.category_slug == args.category]
    if args.demo:
        seen: dict[str, bool] = {}
        picked = []
        for s in pool:
            if s.category_slug not in seen:
                seen[s.category_slug] = True
                picked.append(s)
            if len(picked) >= args.demo:
                break
        return picked
    if args.limit:
        return pool[: args.limit]
    return pool


def cmd_publish(args: argparse.Namespace) -> None:
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    specs = build_specs(per_category=args.per_category)
    selected = _select_specs(specs, args)
    formats = args.formats.split(",") if args.formats else None
    print(f"Publishing {len(selected)} books to {CONTENT_DIR} "
          f"(formats={formats or 'all'})...", file=sys.stderr)

    published_index = []
    t0 = time.time()
    for i, spec in enumerate(selected, 1):
        res = publish_book(spec, CONTENT_DIR, formats=formats)
        published_index.append({
            **res.book.catalog_entry(),
            "dir": res.rel_dir,
            "artifacts": res.artifacts,
        })
        print(f"  [{i}/{len(selected)}] {res.book.id} {res.book.title} "
              f"({res.book.estimated_pages} pp.)", file=sys.stderr)

    pub_path = os.path.join(DATA_DIR, "published.json")
    existing = {}
    if os.path.exists(pub_path) and not args.overwrite:
        with open(pub_path, encoding="utf-8") as fh:
            for rec in json.load(fh):
                existing[rec["id"]] = rec
    for rec in published_index:
        existing[rec["id"]] = rec
    with open(pub_path, "w", encoding="utf-8") as fh:
        json.dump(sorted(existing.values(), key=lambda r: r["id"]), fh,
                  ensure_ascii=False, indent=2)

    print(f"Published {len(selected)} books in {time.time()-t0:.1f}s; "
          f"manifest: {pub_path}", file=sys.stderr)


def cmd_stats(args: argparse.Namespace) -> None:
    path = os.path.join(DATA_DIR, "stats.json")
    if not os.path.exists(path):
        print("No stats.json found. Run 'catalog' first.", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        print(fh.read())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="aupub", description="AI-University publishing engine")
    parser.add_argument("--per-category", type=int, default=16,
                        help="books generated per category (default 16 -> 528 books)")
    sub = parser.add_subparsers(dest="command", required=True)

    pc = sub.add_parser("catalog", help="build the full catalog + stats + search index")
    pc.set_defaults(func=cmd_catalog)

    pp = sub.add_parser("publish", help="fully publish books to all formats")
    pp.add_argument("--limit", type=int, default=None, help="publish the first N books")
    pp.add_argument("--demo", type=int, default=None,
                    help="publish one book from each of the first N categories")
    pp.add_argument("--category", type=str, default=None, help="restrict to a category slug")
    pp.add_argument("--ids", type=str, default=None, help="comma-separated book ids")
    pp.add_argument("--formats", type=str, default=None,
                    help="comma-separated subset of md,html,pdf,docx,pptx")
    pp.add_argument("--overwrite", action="store_true",
                    help="overwrite published.json instead of merging")
    pp.set_defaults(func=cmd_publish)

    ps = sub.add_parser("stats", help="print catalog statistics")
    ps.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
