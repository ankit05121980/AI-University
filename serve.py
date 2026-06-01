#!/usr/bin/env python3
"""AI-University portal app server.

Serves the static portal plus a small JSON API so that *every* book in the
catalog (not just the pre-rendered demo corpus) is fully readable online, with
diagrams, and downloadable in all formats — generated on demand by the engine.

Run from the repository root:

    python serve.py            # http://localhost:8000/web/
    python serve.py 9000       # custom port

API
---
    GET /api/health                       -> { ok, books }
    GET /api/book/<id>                     -> full structured content (with SVG)
    GET /api/ask?q=...                     -> { answer, sources[] }
    GET /api/download/<id>/<fmt>           -> file (md|html|pdf|docx|pptx)

The reader requires only the standard library + the engine (pure-Python). The
download endpoints additionally need the export libraries in
``engine/requirements.txt`` (reportlab, python-docx, python-pptx, markdown).
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import threading
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(ROOT, "engine")
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from aupub.catalog import build_specs                      # noqa: E402
from aupub.generators.book import build_book               # noqa: E402
from aupub.knowledge import DOMAINS                         # noqa: E402
from aupub.exporters import markdown as md_exp              # noqa: E402
from aupub.generators.infographics import render_named, TEMPLATE_NAMES  # noqa: E402
from aupub.qa import ask  # noqa: E402
from aupub.studio import parse_diagram  # noqa: E402

# ---------------------------------------------------------------------------
# Catalog + caches
# ---------------------------------------------------------------------------
SPECS = build_specs()
SPEC_BY_ID = {s.id: s for s in SPECS}
FIRST_BOOK_BY_CAT: dict[str, dict] = {}
for _s in SPECS:
    FIRST_BOOK_BY_CAT.setdefault(_s.category_slug, {"id": _s.id, "title": _s.title})

_book_cache: "OrderedDict[str, object]" = OrderedDict()
_cache_lock = threading.Lock()
_CACHE_MAX = 96


def get_book(book_id: str):
    spec = SPEC_BY_ID.get(book_id)
    if not spec:
        return None
    with _cache_lock:
        if book_id in _book_cache:
            _book_cache.move_to_end(book_id)
            return _book_cache[book_id]
    book = build_book(spec)
    with _cache_lock:
        _book_cache[book_id] = book
        while len(_book_cache) > _CACHE_MAX:
            _book_cache.popitem(last=False)
    return book


# ---------------------------------------------------------------------------
# Downloads (generated on demand)
# ---------------------------------------------------------------------------
import tempfile  # noqa: E402

_MIME = {
    "md": "text/markdown; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def render_download(book, fmt: str) -> bytes:
    if fmt == "md":
        return md_exp.render_markdown(book).encode("utf-8")
    if fmt == "html":
        from aupub.exporters import html as html_exp
        return html_exp.render_html(book).encode("utf-8")
    suffix = "." + fmt
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
        path = tf.name
    try:
        if fmt == "pdf":
            from aupub.exporters import pdf as pdf_exp
            pdf_exp.render_pdf(book, path)
        elif fmt == "docx":
            from aupub.exporters import docx_export
            docx_export.render_docx(book, path)
        elif fmt == "pptx":
            from aupub.exporters import pptx_export
            pptx_export.render_pptx(book, path)
        else:
            raise ValueError("unknown format")
        with open(path, "rb") as fh:
            return fh.read()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "AIUniversity/1.0"

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.startswith("/api/"):
            return self.handle_api(path, parse_qs(parsed.query))
        return self.serve_static(path)

    do_HEAD = do_GET

    # ---- API ----
    def handle_api(self, path, qs):
        try:
            if path == "/api/health":
                return self._json(200, {"ok": True, "books": len(SPECS)})
            if path.startswith("/api/book/"):
                book_id = path[len("/api/book/"):]
                book = get_book(book_id)
                if not book:
                    return self._json(404, {"error": "book not found"})
                return self._json(200, book.to_dict(include_content=True))
            if path == "/api/ask":
                q = (qs.get("q", [""])[0]).strip()
                return self._json(200, ask(q))
            if path == "/api/diagram":
                q = qs.get("q", [""])[0]
                ttype = qs.get("type", ["auto"])[0]
                try:
                    pal = int(qs.get("palette", ["0"])[0])
                except ValueError:
                    pal = 0
                parsed = parse_diagram(q)
                chosen = ttype if ttype in TEMPLATE_NAMES else parsed["type"]
                svg = render_named(chosen, parsed["items"], parsed["subject"], pal)
                return self._json(200, {"svg": svg, "type": chosen,
                                        "subject": parsed["subject"], "items": parsed["items"],
                                        "templates": TEMPLATE_NAMES})
            return self._json(404, {"error": "unknown endpoint"})
        except Exception as e:  # never crash the server on a bad request
            return self._json(500, {"error": str(e)})

    # ---- static ----
    def serve_static(self, path):
        if path in ("/", ""):
            path = "/web/index.html"
        rel = path.lstrip("/")
        full = os.path.normpath(os.path.join(ROOT, rel))
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not full.startswith(ROOT) or not os.path.isfile(full):
            return self._json(404, {"error": "not found"})
        ctype = self._guess_type(full)
        try:
            with open(full, "rb") as fh:
                data = fh.read()
        except OSError:
            return self._json(404, {"error": "not found"})
        self._send(200, data, ctype)

    @staticmethod
    def _guess_type(full):
        ext = os.path.splitext(full)[1].lower()
        return {
            ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml", ".pdf": "application/pdf", ".md": "text/markdown; charset=utf-8",
            ".png": "image/png", ".mmd": "text/plain; charset=utf-8",
            ".puml": "text/plain; charset=utf-8", ".drawio": "application/xml; charset=utf-8",
            ".docx": _MIME["docx"], ".pptx": _MIME["pptx"],
        }.get(ext, "application/octet-stream")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"AI-University portal: http://localhost:{port}/web/")
    print(f"Serving {len(SPECS)} books (full read-online + downloads via API). Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
