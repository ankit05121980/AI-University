"""Diagram Studio text parser.

Turns a free-text prompt into a structured diagram spec (type + subject +
items) by understanding the context. Shared by the local app server and the
Vercel serverless function.
"""
from __future__ import annotations

import re


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
