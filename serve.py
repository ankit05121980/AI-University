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
# "Ask anything" index — built from the curated knowledge base (compact + high
# quality) and mapped to representative books/chapters for citation.
# ---------------------------------------------------------------------------
_STOP = set("the a an and or of to in for on with is are be as by that this it its from at "
            "into can will should would which what how why when where who whom your you we "
            "our their they them then than not no do does using use used".split())
_ASK_INDEX: list[dict] = []


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 30]


def build_ask_index() -> None:
    if _ASK_INDEX:
        return
    for slug, d in DOMAINS.items():
        name = d["name"]
        rep = FIRST_BOOK_BY_CAT.get(slug, {"id": "", "title": name})
        base = {"category": name, "book_id": rep["id"], "book_title": rep["title"]}
        for s in _sentences(d.get("overview", "")):
            _ASK_INDEX.append({**base, "chapter": "Overview", "text": s})
        for title, desc in d.get("concepts", []):
            _ASK_INDEX.append({**base, "chapter": title, "text": f"{title}: {desc}"})
        if d.get("architecture"):
            for s in _sentences(d["architecture"]):
                _ASK_INDEX.append({**base, "chapter": "Architecture and Design", "text": s})
        for bp in d.get("best_practices", []):
            _ASK_INDEX.append({**base, "chapter": "Best Practices",
                               "text": f"Best practice for {name}: {bp}"})
        for pf in d.get("pitfalls", []):
            _ASK_INDEX.append({**base, "chapter": "Common Pitfalls",
                               "text": f"A common pitfall in {name}: {pf}"})
        for industry, scenario in d.get("use_cases", []):
            _ASK_INDEX.append({**base, "chapter": "Industry Use Cases",
                               "text": f"{industry}: {scenario}"})
        for term, definition in d.get("glossary", []):
            _ASK_INDEX.append({**base, "chapter": "Glossary",
                               "text": f"{term} — {definition}"})


def _tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in _STOP and len(t) > 1]


def ask(query: str) -> dict:
    build_ask_index()
    terms = _tokens(query)
    if not terms:
        return {"answer": "Please enter a question or a few keywords.", "sources": [], "passages": []}
    scored = []
    for p in _ASK_INDEX:
        text_l = p["text"].lower()
        ch_l = p["chapter"].lower()
        cat_l = p["category"].lower()
        score = 0.0
        for t in terms:
            score += text_l.count(t)
            if t in ch_l:
                score += 3
            if t in cat_l:
                score += 2
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for _, p in scored[:8]]
    if not top:
        return {"answer": f"I couldn't find anything about “{query}” in the library. "
                          "Try different keywords such as a technique, model or category name.",
                "sources": [], "passages": []}
    # Compose an extractive answer from the most relevant, de-duplicated passages.
    seen, answer_bits = set(), []
    for p in top:
        key = p["text"][:60]
        if key in seen:
            continue
        seen.add(key)
        answer_bits.append(p["text"])
        if len(answer_bits) >= 4:
            break
    answer = " ".join(answer_bits)
    # Sources: distinct book + chapter.
    src_seen, sources = set(), []
    for p in top:
        k = (p["book_id"], p["chapter"])
        if k in src_seen:
            continue
        src_seen.add(k)
        sources.append({"book_id": p["book_id"], "book_title": p["book_title"],
                        "chapter": p["chapter"], "category": p["category"],
                        "snippet": p["text"][:220]})
        if len(sources) >= 6:
            break
    return {"answer": answer, "sources": sources, "terms": terms}


# ---------------------------------------------------------------------------
# Diagram Studio: turn a prompt / free text into a professional diagram
# ---------------------------------------------------------------------------
def parse_diagram(text: str) -> dict:
    t = (text or "").strip()
    low = t.lower()
    first = t.split("\n")[0].strip()

    # split a leading "Subject: ..." prefix from the body
    subject = "Diagram"
    body = t
    m = re.match(r"^([^:\n]{2,60}):\s*(.+)$", t, flags=re.S)
    if m and re.search(r",|->|\u2192|\n|;", m.group(2)):
        subject = m.group(1).strip()
        body = m.group(2).strip()
    elif "\n" in t:
        subject = first[:54]

    def split_items(s):
        return re.split(r"->|\u2192|\u27a1|\n|;|,|\bthen\b|\bnext\b|\bfollowed by\b", s, flags=re.I)

    if "->" in body or "\u2192" in body or "\u27a1" in body:
        kind = "flow_h"; raw = re.split(r"->|\u2192|\u27a1", body)
    elif re.search(r"\bvs\b|versus|compare|comparison|pros and cons", low):
        kind = "matrix"; raw = re.split(r"\bvs\b|versus|,|\n|;", body, flags=re.I)
    elif re.search(r"\bcycle\b|\bloop\b|iterat|continuous|feedback", low):
        kind = "cycle"; raw = split_items(body)
    elif re.search(r"timeline|milestone|phases?\b", low):
        kind = "timeline"; raw = split_items(body)
    elif re.search(r"roadmap|quarter|\bq[1-4]\b", low):
        kind = "roadmap"; raw = split_items(body)
    elif re.search(r"architect|layers?|stack|tiers?|components?", low):
        kind = "layered"; raw = split_items(body)
    elif re.search(r"hierarch|\btree\b|org ?chart|breakdown|taxonomy", low):
        kind = "tree"; raw = split_items(body)
    elif re.search(r"funnel|conversion|\bstages?\b", low):
        kind = "funnel"; raw = split_items(body)
    elif re.search(r"pyramid", low):
        kind = "pyramid"; raw = split_items(body)
    elif re.search(r"mind ?map|brainstorm|themes?", low):
        kind = "mindmap"; raw = split_items(body)
    elif re.search(r"\bkpi\b|metrics?|dashboard|scorecard", low):
        kind = "kpi"; raw = split_items(body)
    else:
        lines = [l for l in body.split("\n") if l.strip()]
        if len(lines) >= 3 and sum(bool(re.match(r"^\s*(\d+[.\)]|[-*\u2022])\s+", l)) for l in lines) >= 2:
            kind = "steps"; raw = lines
        elif re.search(r"\bfirst\b|\bthen\b|\bnext\b|\bfinally\b|\bafter\b", low):
            kind = "flow_h"; raw = split_items(body)
        else:
            raw = re.split(r",|;|\n|\band\b", body)
            kind = "radial"

    items = []
    for it in raw:
        it = re.sub(r"^\s*(\d+[.\)]|[-*\u2022])\s*", "", it).strip(" .:-\t")
        if it:
            items.append(it[:54])
    items = items[:8]
    if not items:
        items = [w for w in re.split(r"\s+", body) if len(w) > 3][:6] or ["Concept"]
    if subject == "Diagram" and len(items) >= 2:
        subject = "Overview"
    if kind == "radial" and len(items) > 6:
        kind = "bars"
    return {"type": kind, "subject": subject, "items": items}


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
