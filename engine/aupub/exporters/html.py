"""Render a book's Markdown to a standalone, styled HTML document with live
Mermaid diagram rendering and embedded SVG.
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
color:var(--fg);line-height:1.7;max-width:860px;margin:0 auto;padding:48px 24px;background:var(--bg)}
h1{font-size:2rem;line-height:1.2;margin-top:2.4em;border-bottom:3px solid var(--accent);padding-bottom:.3em}
h2{font-size:1.4rem;margin-top:1.8em;color:#1e293b}
h3{font-size:1.12rem;margin-top:1.4em;color:#334155}
p{margin:.8em 0}
a{color:var(--accent)}
hr{border:none;border-top:1px solid #e2e8f0;margin:2.5em 0}
code{background:#f1f5f9;padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:var(--code);color:#e2e8f0;padding:18px;border-radius:10px;overflow:auto;font-size:.86rem;line-height:1.5}
pre code{background:none;color:inherit;padding:0}
pre.mermaid{background:#f8fafc;color:inherit;border:1px solid #e2e8f0;text-align:center}
table{border-collapse:collapse;width:100%;margin:1.2em 0;font-size:.92rem}
th,td{border:1px solid #e2e8f0;padding:8px 10px;text-align:left}
th{background:#f1f5f9}
blockquote{border-left:4px solid var(--accent);margin:1em 0;padding:.3em 1em;color:var(--muted);background:#f8fafc}
.diagram-svg{text-align:center;margin:1.4em 0}
.cover{text-align:center;padding:40px 0;border-bottom:3px solid var(--accent)}
ul,ol{padding-left:1.4em}
"""


def render_html(book: Book, *, markdown_source: str | None = None) -> str:
    src = markdown_source if markdown_source is not None else render_markdown(book)
    html_body = md.markdown(
        src,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "md_in_html"],
    )
    # Convert mermaid code fences into mermaid-renderable blocks.
    html_body = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<pre class="mermaid">\1</pre>',
        html_body,
        flags=re.DOTALL,
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
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
</body>
</html>
"""
