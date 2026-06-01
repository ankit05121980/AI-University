"""'Ask Anything' question answering over the knowledge base.

Builds a compact, high-quality passage index from the curated domain knowledge
and maps answers to representative books/chapters for citation. Shared by the
local app server and the Vercel serverless function.
"""
from __future__ import annotations

import re

from .catalog import build_specs
from .knowledge import DOMAINS

_STOP = set(
    "the a an and or of to in for on with is are be as by that this it its from at "
    "into can will should would which what how why when where who whom your you we "
    "our their they them then than not no do does using use used".split()
)

_SPECS = build_specs()
_FIRST_BOOK_BY_CAT: dict[str, dict] = {}
for _s in _SPECS:
    _FIRST_BOOK_BY_CAT.setdefault(_s.category_slug, {"id": _s.id, "title": _s.title})

_ASK_INDEX: list[dict] = []


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p.strip() for p in parts if len(p.strip()) > 30]


def build_ask_index() -> None:
    if _ASK_INDEX:
        return
    for slug, d in DOMAINS.items():
        name = d["name"]
        rep = _FIRST_BOOK_BY_CAT.get(slug, {"id": "", "title": name})
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
                               "text": f"{term} \u2014 {definition}"})


def _tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in _STOP and len(t) > 1]


def ask(query: str) -> dict:
    build_ask_index()
    terms = _tokens(query)
    if not terms:
        return {"answer": "Please enter a question or a few keywords.", "sources": [], "terms": []}
    scored = []
    for p in _ASK_INDEX:
        text_l = p["text"].lower(); ch_l = p["chapter"].lower(); cat_l = p["category"].lower()
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
        return {"answer": f"I couldn't find anything about \u201c{query}\u201d in the library. "
                          "Try different keywords such as a technique, model or category name.",
                "sources": [], "terms": terms}
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
