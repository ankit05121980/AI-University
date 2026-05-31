"""Publishing orchestration.

Ties the content engine and exporters together: builds a book, writes all
output formats (Markdown, HTML, PDF, DOCX, PPTX), stores diagram sources and a
per-book manifest, and contributes to the global catalog and search index.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

from .catalog import BookSpec
from .exporters import (
    diagram_files, docx_export, html as html_exporter, markdown as md_exporter,
    pdf as pdf_exporter, pptx_export,
)
from .generators.book import build_book
from .models import Book

FORMATS = ["md", "html", "pdf", "docx", "pptx"]


@dataclass
class PublishResult:
    book: Book
    rel_dir: str
    artifacts: dict[str, str]


def _book_dir(content_root: str, book: Book) -> str:
    return os.path.join(content_root, book.category_slug, book.slug)


def publish_book(spec: BookSpec, content_root: str, *,
                 formats: list[str] | None = None,
                 write_content_json: bool = True) -> PublishResult:
    formats = formats or FORMATS
    book = build_book(spec)
    out_dir = _book_dir(content_root, book)
    os.makedirs(out_dir, exist_ok=True)
    artifacts: dict[str, str] = {}

    markdown_src = md_exporter.render_markdown(book)

    if "md" in formats:
        p = os.path.join(out_dir, f"{book.slug}.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(markdown_src)
        artifacts["md"] = os.path.relpath(p, content_root)

    if "html" in formats:
        p = os.path.join(out_dir, f"{book.slug}.html")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html_exporter.render_html(book, markdown_source=markdown_src))
        artifacts["html"] = os.path.relpath(p, content_root)

    if "pdf" in formats:
        p = os.path.join(out_dir, f"{book.slug}.pdf")
        pdf_exporter.render_pdf(book, p)
        artifacts["pdf"] = os.path.relpath(p, content_root)

    if "docx" in formats:
        p = os.path.join(out_dir, f"{book.slug}.docx")
        docx_export.render_docx(book, p)
        artifacts["docx"] = os.path.relpath(p, content_root)

    if "pptx" in formats:
        p = os.path.join(out_dir, f"{book.slug}.pptx")
        pptx_export.render_pptx(book, p)
        artifacts["pptx"] = os.path.relpath(p, content_root)

    # Diagram sources stored separately.
    diagrams_dir = os.path.join(out_dir, "diagrams")
    diagram_index = diagram_files.write_diagram_sources(book, diagrams_dir)
    artifacts["diagrams_dir"] = os.path.relpath(diagrams_dir, content_root)

    # Structured content for the web viewer.
    if write_content_json:
        p = os.path.join(out_dir, "content.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(book.to_dict(include_content=True), fh, ensure_ascii=False)
        artifacts["content"] = os.path.relpath(p, content_root)

    # Per-book manifest.
    manifest = {
        **book.catalog_entry(),
        "artifacts": artifacts,
        "diagram_index": diagram_index,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    return PublishResult(book=book, rel_dir=os.path.relpath(out_dir, content_root),
                         artifacts=artifacts)


def build_search_record(book: Book, rel_dir: str) -> dict:
    """A compact, searchable record (used to build the global search index)."""
    chapter_titles = [c.title for c in book.chapters]
    text_blob = " ".join(
        [book.title, book.subtitle, book.category, book.front_matter.executive_summary]
        + chapter_titles
        + [t for t in book.back_matter.index_terms]
    )
    return {
        "id": book.id,
        "slug": book.slug,
        "title": book.title,
        "subtitle": book.subtitle,
        "category": book.category,
        "category_slug": book.category_slug,
        "level": book.level,
        "authors": book.authors,
        "keywords": book.keywords,
        "chapters": chapter_titles,
        "dir": rel_dir,
        "pages": book.estimated_pages,
        "words": book.word_count,
        "text": text_blob[:4000],
    }
