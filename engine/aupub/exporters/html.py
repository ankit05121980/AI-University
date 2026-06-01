"""Render a book's Markdown to a standalone, styled HTML document with
fully-inlined, self-contained SVG diagrams (no external renderer required).
"""
from __future__ import annotations

import re

import markdown as md

from ..models import Book
from .markdown import render_markdown

_CSS = """
:root{--fg:#0f172a;--muted:#475569;--accent:#4338ca;--bg:#ffffff;--code:#0b1021;}
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,Arial,sans-serif;
color:var(--fg);line-height:1.7;max-width:880px;margin:0 auto;padding:48px 24px;background:var(--bg)}
h1{font-size:2rem;line-height:1.2;margin-top:2.4em;border-bottom:3px solid var(--accent);padding-bottom:.3em}
h2{font-size:1.4rem;margin-top:1.8em;color:#1e293b}
h3{font-size:1.12rem;margin-top:1.4em;color:#334155}
p{margin:.8em 0}
a{color:var(--accent)}
hr{border:none;border-top:1px solid #e2e8f0;margin:2.5em 0}
code{background:#f1f5f9;padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:var(--code);color:#e2e8f0;padding:18px;border-radius:10px;overflow:auto;font-size:.86rem;line-height:1.5}
pre code{background:none;color:inherit;padding:0}
table{border-collapse:collapse;width:100%;margin:1.2em 0;font-size:.92rem}
th,td{border:1px solid #e2e8f0;padding:8px 10px;text-align:left}
th{background:#f1f5f9}
blockquote{border-left:4px solid var(--accent);margin:1em 0;padding:.3em 1em;color:var(--muted);background:#f8fafc}
.diagram-svg{text-align:center;margin:1.4em 0;border:1px solid #e2e8f0;border-radius:14px;padding:16px;background:#f8fafc}
.diagram-svg svg{max-width:100%;height:auto}
ul,ol{padding-left:1.4em}
"""


def render_html(book: Book, *, markdown_source: str | None = None) -> str:
    # Always render diagrams as inlined SVG so the HTML is self-contained.
    src = render_markdown(book, diagram_mode="svg")
    html_body = md.markdown(
        src,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "md_in_html"],
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{book.title} — AI-University Press</title>
<meta name="description" content="{book.subtitle}">
<style>{_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>
"""
