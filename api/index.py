"""Vercel Python serverless function for the AI-University API.

Handles all `/api/*` routes (rewritten to this function by vercel.json):

    GET /api/health             -> { ok, books }
    GET /api/book/<id>          -> full structured book content (with diagrams)
    GET /api/ask?q=...          -> { answer, sources[] }
    GET /api/diagram?q=&type=&palette=  -> { svg, type, subject, items }

All generation is pure-Python (no external dependencies), so the function is
small and fast. The engine package is bundled via `includeFiles` in
vercel.json and imported from the repository's ``engine`` directory.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote, urlparse

# Make the engine importable (bundled via vercel.json includeFiles).
_ENGINE = os.path.join(os.path.dirname(__file__), "..", "engine")
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from aupub.catalog import build_specs                       # noqa: E402
from aupub.generators.book import build_book                # noqa: E402
from aupub.generators.infographics import render_named, TEMPLATE_NAMES  # noqa: E402
from aupub.qa import ask                                    # noqa: E402
from aupub.studio import parse_diagram                      # noqa: E402

SPEC_BY_ID = {s.id: s for s in build_specs()}
_book_cache: dict[str, object] = {}


def get_book(book_id: str):
    if book_id in _book_cache:
        return _book_cache[book_id]
    spec = SPEC_BY_ID.get(book_id)
    if not spec:
        return None
    book = build_book(spec)
    if len(_book_cache) < 64:
        _book_cache[book_id] = book
    return book


class handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj: dict, cache: int = 600):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", f"public, max-age={cache}")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        qs = parse_qs(parsed.query)
        try:
            if "/api/health" in path:
                return self._send(200, {"ok": True, "books": len(SPEC_BY_ID)}, cache=60)
            if "/api/book/" in path:
                book_id = path.split("/api/book/", 1)[1].strip("/")
                book = get_book(book_id)
                if not book:
                    return self._send(404, {"error": "book not found"})
                return self._send(200, book.to_dict(include_content=True))
            if "/api/ask" in path:
                return self._send(200, ask((qs.get("q", [""])[0]).strip()), cache=120)
            if "/api/diagram" in path:
                q = qs.get("q", [""])[0]
                ttype = qs.get("type", ["auto"])[0]
                try:
                    pal = int(qs.get("palette", ["0"])[0])
                except ValueError:
                    pal = 0
                parsed_d = parse_diagram(q)
                chosen = ttype if ttype in TEMPLATE_NAMES else parsed_d["type"]
                svg = render_named(chosen, parsed_d["items"], parsed_d["subject"], pal)
                return self._send(200, {"svg": svg, "type": chosen,
                                        "subject": parsed_d["subject"], "items": parsed_d["items"],
                                        "templates": TEMPLATE_NAMES}, cache=120)
            return self._send(404, {"error": "unknown endpoint", "path": path})
        except Exception as exc:  # never 500 silently
            return self._send(500, {"error": str(exc)}, cache=0)

    def log_message(self, *args):  # quiet
        pass
