"""Write each diagram's source to a separate file in its native format."""
from __future__ import annotations

import os

from ..models import Book, slugify

_EXT = {"mermaid": "mmd", "plantuml": "puml", "svg": "svg", "drawio": "drawio"}


def write_diagram_sources(book: Book, diagrams_dir: str) -> list[dict]:
    """Write all diagram sources under ``diagrams_dir`` and return an index."""
    os.makedirs(diagrams_dir, exist_ok=True)
    index: list[dict] = []
    n = 0
    for ch in book.chapters:
        for d in ch.diagrams:
            n += 1
            ext = _EXT.get(d.fmt, "txt")
            fname = f"fig-{n:03d}-{slugify(d.kind)}.{ext}"
            with open(os.path.join(diagrams_dir, fname), "w", encoding="utf-8") as fh:
                fh.write(d.source)
            index.append({
                "figure": n,
                "chapter": ch.number,
                "title": d.title,
                "kind": d.kind,
                "fmt": d.fmt,
                "file": fname,
                "caption": d.caption,
            })
    return index
