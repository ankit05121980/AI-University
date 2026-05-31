"""Professional infographic SVG library.

Provides a large catalogue of self-contained, dependency-free SVG infographic
templates (flow, layered, funnel, pyramid, donut, bars, matrix, timeline,
steps, concentric, honeycomb, pillars, ladder, cycle, swimlane, KPI, venn,
mindmap, tree, radial, sequence, gauge, roadmap) rendered with curated
professional colour palettes.

A diagram's template and palette are selected deterministically from the
caller's seeded RNG, so each figure looks distinct while remaining
reproducible. With 24 templates x 12 palettes there are 288 base patterns,
plus per-figure label/value variation, giving well over 200 visually distinct
infographics across the library.
"""
from __future__ import annotations

import math
import random
from xml.sax.saxutils import escape

W, H = 840, 460
PAD = 28

# --- professional palettes (each: list of saturated hexes) ------------------
PALETTES: list[list[str]] = [
    ["#4338ca", "#6d28d9", "#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd"],  # indigo
    ["#0e7490", "#0891b2", "#0ea5e9", "#38bdf8", "#0284c7", "#075985"],  # ocean
    ["#047857", "#059669", "#10b981", "#34d399", "#0d9488", "#14b8a6"],  # emerald
    ["#b45309", "#d97706", "#f59e0b", "#ea580c", "#f97316", "#fb923c"],  # sunset
    ["#9f1239", "#be123c", "#e11d48", "#f43f5e", "#fb7185", "#db2777"],  # rose
    ["#1e3a8a", "#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#1e40af"],  # royal
    ["#334155", "#475569", "#64748b", "#0f172a", "#1e293b", "#94a3b8"],  # slate
    ["#6b21a8", "#7e22ce", "#9333ea", "#a21caf", "#c026d3", "#d946ef"],  # berry
    ["#0f766e", "#14b8a6", "#2dd4bf", "#65a30d", "#84cc16", "#0d9488"],  # teal-lime
    ["#9d174d", "#db2777", "#ec4899", "#f472b6", "#fb7185", "#e11d48"],  # coral
    ["#14532d", "#166534", "#15803d", "#16a34a", "#22c55e", "#4ade80"],  # forest
    ["#0f172a", "#1e40af", "#0e7490", "#b45309", "#9f1239", "#4338ca"],  # corporate
]

INK = "#0f172a"
MUTED = "#64748b"
BG = "#ffffff"
PANEL = "#f8fafc"

_DEFS = (
    '<defs>'
    '<marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">'
    '<path d="M0,0 L7,3 L0,6 z" fill="#94a3b8"/></marker>'
    '<marker id="arw" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">'
    '<path d="M0,0 L7,3 L0,6 z" fill="#ffffff"/></marker>'
    '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.16"/></filter>'
    '</defs>'
)


# --- helpers ----------------------------------------------------------------

def _short(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def _txt(x, y, s, fs=12, fill=INK, anchor="middle", weight="600"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{fs}" '
            f'font-weight="{weight}" fill="{fill}" dominant-baseline="middle">{escape(str(s))}</text>')


def _wrap(s, cpl, maxlines):
    words = str(s).split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= cpl or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
            if len(lines) >= maxlines:
                cur = ""; break
    if cur and len(lines) < maxlines:
        lines.append(cur)
    return lines or [str(s)]


def _mtext(cx, cy, lines, fs, fill, weight="600"):
    n = len(lines); lh = fs * 1.15; y0 = cy - (n - 1) * lh / 2
    return "".join(_txt(cx, y0 + i * lh, ln, fs, fill, "middle", weight) for i, ln in enumerate(lines))


def _rect(x, y, w, h, fill, rx=10, stroke="none", sw=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}"{st}/>'


def _arrow(x1, y1, x2, y2, white=False, color="#94a3b8"):
    mk = "arw" if white else "ar"
    col = "#ffffff" if white else color
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" '
            f'stroke-width="2" marker-end="url(#{mk})"/>')


def _labels(domain, n, rng):
    ls = [c[0] for c in domain.get("concepts", [])]
    if not ls:
        ls = ["Input", "Process", "Store", "Serve", "Monitor", "Govern"]
    start = 0 if domain.get("_ordered") else rng.randrange(len(ls))
    out = [ls[(start + i) % len(ls)] for i in range(n)]
    return out


def _vals(rng, n, lo=35, hi=100):
    return [rng.randint(lo, hi) for _ in range(n)]


def _box(x, y, w, h, fill, label, fg="#ffffff", fs=12, rx=11, sub=None):
    out = [f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}" filter="url(#sh)"/>']
    cpl = max(6, int((w - 12) / (fs * 0.54)))
    maxlines = 3 if h >= 56 else 2
    lines = _wrap(label, cpl, maxlines)
    # shrink font a touch if it overflowed the line budget
    if sum(len(l) for l in lines) < len(str(label)) and fs > 9:
        fs2 = fs - 1.5
        cpl = max(6, int((w - 10) / (fs2 * 0.54)))
        lines = _wrap(label, cpl, maxlines + 1)
        fs = fs2
    if sub:
        out.append(_mtext(x + w / 2, y + h / 2 - 8, lines, fs, fg))
        out.append(_txt(x + w / 2, y + h / 2 + 11, _short(sub, 24), fs - 2, fg, weight="500"))
    else:
        out.append(_mtext(x + w / 2, y + h / 2, lines, fs, fg))
    return "".join(out)


# --- templates: each returns inner SVG string -------------------------------
# signature: fn(domain, title, pal, rng) -> str

def t_flow_h(domain, title, pal, rng):
    ls = _labels(domain, 5, rng)
    n = len(ls); out = []
    bw, gap = 130, 28
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = H / 2 - 34
    for i, l in enumerate(ls):
        x = x0 + i * (bw + gap)
        out.append(_box(x, y, bw, 68, pal[i % len(pal)], l, fs=12))
        if i:
            out.append(_arrow(x - gap, y + 34, x, y + 34))
    out.append(_txt(W / 2, y + 104, "end-to-end flow", 11, MUTED, weight="500"))
    return "".join(out)


def t_flow_v(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    bh, gap = 52, 22; n = len(ls)
    total = n * bh + (n - 1) * gap
    y0 = (H - total) / 2 + 14
    cx = W / 2
    for i, l in enumerate(ls):
        y = y0 + i * (bh + gap)
        out.append(_box(cx - 150, y, 300, bh, pal[i % len(pal)], l, fs=12))
        if i:
            out.append(_arrow(cx, y - gap, cx, y))
    return "".join(out)


def t_layered(domain, title, pal, rng):
    tiers = [("Experience", _labels(domain, 2, rng)),
             ("Platform", _labels(domain, 4, rng)),
             ("Data & Operations", ["Store", "Index", "Observability", "Security"])]
    out = []; y = 64; lh = 104
    for li, (name, boxes) in enumerate(tiers):
        out.append(_rect(PAD, y, W - 2 * PAD, lh, PANEL, 14, "#e2e8f0", 1))
        out.append(_txt(PAD + 14, y + 16, name, 11, MUTED, "start", "700"))
        m = len(boxes); bw = (W - 2 * PAD - 28 - (m - 1) * 14) / m
        for bi, b in enumerate(boxes):
            x = PAD + 14 + bi * (bw + 14)
            out.append(_box(x, y + 32, bw, 52, pal[(li + bi) % len(pal)], b, fs=11))
        y += lh + 18
    return "".join(out)


def t_sequence(domain, title, pal, rng):
    actors = ["User", "Gateway", "Service", "Store"]
    msgs = [(0, 1, "request"), (1, 2, "dispatch"), (2, 3, "query"), (3, 2, "data"), (2, 1, "result"), (1, 0, "response")]
    out = []; n = len(actors)
    xs = [PAD + 60 + i * ((W - 2 * PAD - 120) / (n - 1)) for i in range(n)]
    top, bot = 60, H - 36
    for i, a in enumerate(actors):
        out.append(_box(xs[i] - 62, top, 124, 34, pal[i % len(pal)], a, fs=11))
        out.append(f'<line x1="{xs[i]:.0f}" y1="{top+34}" x2="{xs[i]:.0f}" y2="{bot}" stroke="#cbd5e1" stroke-width="1.4" stroke-dasharray="4 4"/>')
    y = top + 64
    for a, b, lbl in msgs:
        out.append(_arrow(xs[a], y, xs[b], y, color=pal[0]))
        out.append(_txt((xs[a] + xs[b]) / 2, y - 9, lbl, 10, MUTED, weight="500"))
        y += 40
    return "".join(out)


def t_radial(domain, title, pal, rng):
    ls = _labels(domain, 6, rng); out = []
    cx, cy = W / 2, H / 2 + 8
    out.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="{INK}"/>')
    out.append(_mtext(cx, cy, _wrap(domain["name"], 13, 2), 12, "#fff"))
    n = len(ls)
    for i, l in enumerate(ls):
        ang = 2 * math.pi * i / n - math.pi / 2
        bx = cx + 270 * math.cos(ang); by = cy + 150 * math.sin(ang)
        out.append(_arrow(cx + 52 * math.cos(ang), cy + 52 * math.sin(ang), bx - 26 * math.cos(ang), by - 14 * math.sin(ang)))
        out.append(_box(bx - 78, by - 23, 156, 46, pal[i % len(pal)], l, fs=11))
    return "".join(out)


def t_mindmap(domain, title, pal, rng):
    ls = _labels(domain, 6, rng); out = []
    cx, cy = W / 2, H / 2 + 6
    out.append(_box(cx - 90, cy - 26, 180, 52, INK, domain["name"], fs=13))
    left = ls[:3]; right = ls[3:6]
    for side, items in ((-1, left), (1, right)):
        for i, l in enumerate(items):
            by = cy - 110 + i * 110
            bx = cx + side * 250
            out.append(f'<path d="M{cx + side*90:.0f},{cy:.0f} C{cx+side*170:.0f},{cy:.0f} {bx-side*80:.0f},{by:.0f} {bx-side*78:.0f},{by:.0f}" fill="none" stroke="#cbd5e1" stroke-width="2"/>')
            out.append(_box(bx - 78, by - 22, 156, 44, pal[(i + (0 if side < 0 else 3)) % len(pal)], l, fs=11))
    return "".join(out)


def t_funnel(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    n = len(ls); topw = 460; y = 70; h = 52; gap = 12
    for i, l in enumerate(ls):
        w = topw * (1 - i * 0.16)
        x = (W - w) / 2
        out.append(f'<polygon points="{x:.0f},{y:.0f} {x+w:.0f},{y:.0f} {x+w-26:.0f},{y+h:.0f} {x+26:.0f},{y+h:.0f}" fill="{pal[i % len(pal)]}"/>')
        out.append(_mtext(W / 2, y + h / 2, _wrap(l, max(10, int((w - 40) / 6.5)), 2), 12, "#fff"))
        y += h + gap
    return "".join(out)


def t_pyramid(domain, title, pal, rng):
    ls = _labels(domain, 4, rng); out = []
    n = len(ls); baseW = 480; h = 66; y = H - 60
    for i, l in enumerate(ls):
        w = baseW * (1 - i / n)
        x = (W - w) / 2
        out.append(f'<polygon points="{W/2:.0f},{y-h:.0f} {x:.0f},{y:.0f} {x+w:.0f},{y:.0f}" fill="{pal[i % len(pal)]}"/>' if i == n - 1 else _rect(x, y - h, w, h - 6, pal[i % len(pal)], 4))
        out.append(_mtext(W / 2, y - h / 2, _wrap(l, 26, 2), 12, "#fff"))
        y -= h
    return "".join(out)


def t_donut(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); vals = _vals(rng, len(ls), 10, 40)
    tot = sum(vals); out = []
    cx, cy, r, rin = 250, H / 2 + 8, 120, 66
    a0 = -90
    for i, (l, v) in enumerate(zip(ls, vals)):
        ang = 360 * v / tot
        a1 = a0 + ang
        large = 1 if ang > 180 else 0
        x0 = cx + r * math.cos(math.radians(a0)); y0 = cy + r * math.sin(math.radians(a0))
        x1 = cx + r * math.cos(math.radians(a1)); y1 = cy + r * math.sin(math.radians(a1))
        out.append(f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} Z" fill="{pal[i % len(pal)]}"/>')
        a0 = a1
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{rin}" fill="{BG}"/>')
    out.append(_txt(cx, cy, f"{len(ls)} parts", 13, INK))
    lx, ly = 470, cy - 90
    for i, (l, v) in enumerate(zip(ls, vals)):
        out.append(_rect(lx, ly + i * 36, 16, 16, pal[i % len(pal)], 4))
        out.append(_txt(lx + 26, ly + i * 36 + 8, f"{_short(l, 52)}  ({round(100*v/tot)}%)", 11, INK, "start", "500"))
    return "".join(out)


def t_bars(domain, title, pal, rng):
    ls = _labels(domain, 6, rng); vals = _vals(rng, len(ls), 30, 100); out = []
    n = len(ls); bw = 70; gap = 24; total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2; base = H - 80; maxh = 230
    out.append(f'<line x1="{x0-16}" y1="{base}" x2="{x0+total+16}" y2="{base}" stroke="#cbd5e1" stroke-width="1.5"/>')
    for i, (l, v) in enumerate(zip(ls, vals)):
        bh = maxh * v / 100; x = x0 + i * (bw + gap)
        out.append(_rect(x, base - bh, bw, bh, pal[i % len(pal)], 8))
        out.append(_txt(x + bw / 2, base - bh - 12, f"{v}", 11, INK))
        out.append(_mtext(x + bw / 2, base + 18, _wrap(l, 11, 2), 9, MUTED, "500"))
    return "".join(out)


def t_matrix(domain, title, pal, rng):
    ls = _labels(domain, 4, rng); out = []
    cx, cy = W / 2, H / 2 + 14; s = 150
    quads = [(cx - s, cy - s), (cx, cy - s), (cx - s, cy), (cx, cy)]
    for i, (qx, qy) in enumerate(quads):
        out.append(_rect(qx + 3, qy + 3, s - 6, s - 6, pal[i % len(pal)], 12))
        out.append(_mtext(qx + s / 2, qy + s / 2, _wrap(ls[i], 16, 3), 12, "#fff"))
    out.append(_txt(cx, cy - s - 12, "High impact", 10, MUTED, weight="600"))
    out.append(_txt(cx, cy + s + 16, "Low impact", 10, MUTED, weight="600"))
    out.append(f'<text x="{cx-s-12}" y="{cy}" text-anchor="middle" font-size="10" fill="{MUTED}" transform="rotate(-90 {cx-s-12} {cy})">Low effort</text>')
    out.append(f'<text x="{cx+s+12}" y="{cy}" text-anchor="middle" font-size="10" fill="{MUTED}" transform="rotate(90 {cx+s+12} {cy})">High effort</text>')
    return "".join(out)


def t_timeline(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    y = H / 2; n = len(ls)
    x0 = PAD + 40; x1 = W - PAD - 40
    out.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#cbd5e1" stroke-width="3"/>')
    for i, l in enumerate(ls):
        x = x0 + (x1 - x0) * i / (n - 1)
        up = i % 2 == 0
        out.append(f'<circle cx="{x:.0f}" cy="{y}" r="9" fill="{pal[i % len(pal)]}"/>')
        by = y - 92 if up else y + 24
        out.append(f'<line x1="{x:.0f}" y1="{y}" x2="{x:.0f}" y2="{by + (60 if up else 0):.0f}" stroke="#cbd5e1" stroke-width="1.4"/>')
        out.append(_box(x - 70, by, 140, 52, pal[i % len(pal)], l, fs=11, sub=f"Phase {i+1}"))
    return "".join(out)


def t_steps(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    n = len(ls); y = H / 2 - 30; bw = 132; gap = 30
    total = n * bw + (n - 1) * gap; x0 = (W - total) / 2
    for i, l in enumerate(ls):
        x = x0 + i * (bw + gap); c = pal[i % len(pal)]
        out.append(_rect(x, y, bw, 70, c, 12))
        out.append(f'<circle cx="{x+24:.0f}" cy="{y+24:.0f}" r="15" fill="#ffffff"/>')
        out.append(_txt(x + 24, y + 24, str(i + 1), 13, c))
        out.append(_mtext(x + bw / 2, y + 48, _wrap(l, 18, 2), 10.5, "#fff"))
        if i:
            out.append(_arrow(x - gap, y + 35, x, y + 35))
    return "".join(out)


def t_concentric(domain, title, pal, rng):
    ls = _labels(domain, 4, rng); out = []
    cx, cy = W / 2, H / 2 + 8
    for i in range(len(ls)):
        r = 150 - i * 34
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{pal[i % len(pal)]}"/>')
        out.append(_mtext(cx, cy - r + 22, _wrap(ls[i], 30, 2), 11, "#fff"))
    return "".join(out)


def t_honeycomb(domain, title, pal, rng):
    ls = _labels(domain, 7, rng); out = []
    cx, cy = W / 2, H / 2 + 8; r = 52
    def hexp(x, y):
        pts = [(x + r * math.cos(math.radians(60 * k - 30)), y + r * math.sin(math.radians(60 * k - 30))) for k in range(6)]
        return " ".join(f"{px:.0f},{py:.0f}" for px, py in pts)
    dx = r * 1.74; dy = r * 1.5
    positions = [(0, 0), (-dx, 0), (dx, 0), (-dx / 2, -dy), (dx / 2, -dy), (-dx / 2, dy), (dx / 2, dy)]
    for i, (ox, oy) in enumerate(positions[:len(ls)]):
        x = cx + ox; y = cy + oy
        out.append(f'<polygon points="{hexp(x, y)}" fill="{pal[i % len(pal)]}"/>')
        out.append(_mtext(x, y, _wrap(ls[i], 11, 2), 9.5, "#fff"))
    return "".join(out)


def t_pillars(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    n = len(ls); bw = 120; gap = 26; total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2; base = H - 70; ph = 250
    for i, l in enumerate(ls):
        x = x0 + i * (bw + gap); c = pal[i % len(pal)]
        out.append(_rect(x, base - ph, bw, ph, c, 10))
        out.append(_rect(x - 8, base - ph - 14, bw + 16, 18, c, 6))
        for s in c.split():
            pass
        out.append(_mtext(x + bw / 2, base - ph / 2, _wrap(l, 16, 3), 11, "#fff"))
    out.append(f'<rect x="{x0-20}" y="{base}" width="{total+40}" height="12" rx="4" fill="{INK}"/>')
    return "".join(out)


def t_ladder(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    n = len(ls); sw = 150; sh = 50; x = PAD + 20; base = H - 60
    for i, l in enumerate(ls):
        y = base - (i + 1) * sh
        out.append(_rect(x, y, sw, sh - 6, pal[i % len(pal)], 8))
        out.append(_mtext(x + sw / 2, y + (sh - 6) / 2, _wrap(l, 22, 2), 11, "#fff"))
        x += sw - 20
    out.append(_txt(W - 150, 80, "maturity \u2197", 12, MUTED, weight="600"))
    return "".join(out)


def t_cycle(domain, title, pal, rng):
    ls = _labels(domain, 5, rng); out = []
    cx, cy, r = W / 2, H / 2 + 8, 130; n = len(ls)
    for i, l in enumerate(ls):
        ang = 2 * math.pi * i / n - math.pi / 2
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        out.append(_box(x - 72, y - 22, 144, 44, pal[i % len(pal)], l, fs=11))
    for i in range(n):
        a0 = 2 * math.pi * i / n - math.pi / 2 + 0.42
        a1 = 2 * math.pi * (i + 1) / n - math.pi / 2 - 0.42
        x0 = cx + (r - 30) * math.cos(a0); y0 = cy + (r - 30) * math.sin(a0)
        x1 = cx + (r - 30) * math.cos(a1); y1 = cy + (r - 30) * math.sin(a1)
        out.append(f'<path d="M{x0:.0f},{y0:.0f} A{r-30},{r-30} 0 0 1 {x1:.0f},{y1:.0f}" fill="none" stroke="#cbd5e1" stroke-width="2" marker-end="url(#ar)"/>')
    out.append(_txt(cx, cy, "continuous\ncycle".split("\n")[0], 12, MUTED))
    return "".join(out)


def t_swimlane(domain, title, pal, rng):
    lanes = ["Business", "Application", "Data"]; out = []
    y = 64; lh = 100
    for li, lane in enumerate(lanes):
        out.append(_rect(PAD, y, W - 2 * PAD, lh - 10, PANEL, 10, "#e2e8f0", 1))
        out.append(_txt(PAD + 12, y + (lh - 10) / 2, lane, 11, MUTED, "start", "700"))
        steps = _labels(domain, 4, rng)
        for si, s in enumerate(steps):
            x = PAD + 130 + si * 160
            out.append(_box(x, y + 18, 140, lh - 46, pal[(li + si) % len(pal)], s, fs=10.5))
            if si:
                out.append(_arrow(x - 20, y + (lh - 10) / 2, x, y + (lh - 10) / 2))
        y += lh
    return "".join(out)


def t_kpi(domain, title, pal, rng):
    ls = _labels(domain, 4, rng); vals = _vals(rng, 4, 40, 99); out = []
    n = 4; cw = (W - 2 * PAD - (n - 1) * 18) / n
    for i in range(n):
        x = PAD + i * (cw + 18); c = pal[i % len(pal)]
        out.append(_rect(x, 90, cw, 150, PANEL, 14, "#e2e8f0", 1))
        out.append(_rect(x, 90, cw, 8, c, 0))
        out.append(_txt(x + cw / 2, 150, f"{vals[i]}%", 30, c, weight="800"))
        out.append(_mtext(x + cw / 2, 198, _wrap(ls[i], 22, 2), 11, MUTED, "600"))
    return "".join(out)


def t_venn(domain, title, pal, rng):
    ls = _labels(domain, 3, rng); out = []
    cx, cy, r = W / 2, H / 2 + 8, 110
    pts = [(cx - 58, cy - 30), (cx + 58, cy - 30), (cx, cy + 60)]
    for i, (x, y) in enumerate(pts):
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{pal[i % len(pal)]}" fill-opacity="0.55"/>')
    labelpos = [(cx - 110, cy - 70), (cx + 110, cy - 70), (cx, cy + 130)]
    for i, (x, y) in enumerate(labelpos):
        out.append(_mtext(x, y, _wrap(ls[i], 20, 2), 12, INK))
    return "".join(out)


def t_tree(domain, title, pal, rng):
    root = domain["name"]; kids = _labels(domain, 4, rng); out = []
    cx = W / 2
    out.append(_box(cx - 90, 70, 180, 48, INK, root, fs=12))
    n = len(kids); span = W - 2 * PAD - 160
    for i, k in enumerate(kids):
        x = PAD + 80 + (span) * i / (n - 1) if n > 1 else cx
        y = 210
        out.append(f'<path d="M{cx:.0f},118 C{cx:.0f},170 {x:.0f},160 {x:.0f},{y:.0f}" fill="none" stroke="#cbd5e1" stroke-width="2"/>')
        out.append(_box(x - 78, y, 156, 46, pal[i % len(pal)], k, fs=11))
        leaf = _labels(domain, 1, rng)[0]
        out.append(f'<line x1="{x:.0f}" y1="{y+46}" x2="{x:.0f}" y2="{y+86}" stroke="#cbd5e1" stroke-width="1.6"/>')
        out.append(_box(x - 70, y + 86, 140, 40, PANEL, leaf, fg=INK, fs=10))
    return "".join(out)


def t_gauge(domain, title, pal, rng):
    out = []; cx, cy, r = W / 2, H / 2 + 60, 150
    val = rng.randint(45, 95)
    segs = 5
    for i in range(segs):
        a0 = 180 - 180 * i / segs; a1 = 180 - 180 * (i + 1) / segs
        x0 = cx + r * math.cos(math.radians(a0)); y0 = cy - r * math.sin(math.radians(a0))
        x1 = cx + r * math.cos(math.radians(a1)); y1 = cy - r * math.sin(math.radians(a1))
        out.append(f'<path d="M{x0:.0f},{y0:.0f} A{r},{r} 0 0 1 {x1:.0f},{y1:.0f}" fill="none" stroke="{pal[i % len(pal)]}" stroke-width="26" stroke-linecap="round"/>')
    ang = math.radians(180 - 180 * val / 100)
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + (r-30)*math.cos(ang):.0f}" y2="{cy - (r-30)*math.sin(ang):.0f}" stroke="{INK}" stroke-width="4"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{INK}"/>')
    out.append(_txt(cx, cy - 40, f"{val}%", 26, INK, weight="800"))
    lbl = _labels(domain, 1, rng)[0]
    out.append(_mtext(cx, cy + 30, _wrap(lbl, 46, 2), 12, MUTED, "600"))
    return "".join(out)


def t_roadmap(domain, title, pal, rng):
    ls = _labels(domain, 4, rng); out = []
    y = H / 2 - 26; n = len(ls); seg = (W - 2 * PAD) / n
    for i, l in enumerate(ls):
        x = PAD + i * seg; c = pal[i % len(pal)]
        out.append(f'<polygon points="{x:.0f},{y:.0f} {x+seg-18:.0f},{y:.0f} {x+seg:.0f},{y+30:.0f} {x+seg-18:.0f},{y+60:.0f} {x:.0f},{y+60:.0f} {x+18:.0f},{y+30:.0f}" fill="{c}"/>')
        out.append(_mtext(x + seg / 2, y + 30, _wrap(l, 22, 2), 11, "#fff"))
        out.append(_txt(x + seg / 2, y - 14, f"Q{i+1}", 11, MUTED, weight="700"))
    return "".join(out)


def t_grid_matrix(domain, title, pal, rng):
    rows = _labels(domain, 4, rng); cols = ["Plan", "Build", "Run", "Improve"]; out = []
    gx, gy = 200, 90; cw, ch = (W - gx - PAD) / len(cols), 70
    for ci, c in enumerate(cols):
        out.append(_txt(gx + ci * cw + cw / 2, gy - 12, c, 10.5, MUTED, weight="700"))
    for ri, rlab in enumerate(rows):
        _rl = _wrap(rlab, 26, 2)
        for _li, _ln in enumerate(_rl):
            out.append(_txt(gx - 12, gy + ri * ch + ch / 2 + (_li - (len(_rl) - 1) / 2) * 12, _ln, 10, INK, "end", "600"))
        for ci in range(len(cols)):
            v = rng.randint(0, 5)
            c = pal[(ri + ci) % len(pal)]
            out.append(_rect(gx + ci * cw + 3, gy + ri * ch + 3, cw - 6, ch - 6, c, 8))
            out.append(f'<rect x="{gx+ci*cw+3:.0f}" y="{gy+ri*ch+3:.0f}" width="{cw-6:.0f}" height="{ch-6:.0f}" rx="8" fill="#ffffff" fill-opacity="{(5-v)/8:.2f}"/>')
    return "".join(out)


TEMPLATES = [
    t_flow_h, t_flow_v, t_layered, t_sequence, t_radial, t_mindmap, t_funnel,
    t_pyramid, t_donut, t_bars, t_matrix, t_timeline, t_steps, t_concentric,
    t_honeycomb, t_pillars, t_ladder, t_cycle, t_swimlane, t_kpi, t_venn,
    t_tree, t_gauge, t_roadmap, t_grid_matrix,
]
TEMPLATE_NAMES = [f.__name__[2:] for f in TEMPLATES]

# Map diagram "kind" to a sensible subset of templates (by index into TEMPLATES).
_BY_NAME = {f.__name__[2:]: i for i, f in enumerate(TEMPLATES)}


def _idx(*names):
    return [_BY_NAME[n] for n in names]


KIND_TEMPLATES = {
    "Sequence": _idx("sequence", "swimlane", "flow_v"),
    "Class": _idx("tree", "radial", "mindmap"),
    "Knowledge Graph": _idx("mindmap", "radial", "tree", "honeycomb"),
    "Capability Map": _idx("honeycomb", "matrix", "grid_matrix", "kpi", "pillars"),
    "Operating Model": _idx("swimlane", "layered", "matrix", "pillars", "grid_matrix"),
    "Data Flow": _idx("flow_h", "flow_v", "steps", "timeline"),
    "Application Flow": _idx("flow_h", "steps", "swimlane", "cycle"),
    "Business Process": _idx("flow_h", "swimlane", "steps", "funnel", "timeline"),
    "Data Lineage": _idx("flow_h", "timeline", "tree", "steps"),
    "DevOps Pipeline": _idx("steps", "flow_h", "roadmap", "cycle"),
    "CI/CD Pipeline": _idx("steps", "flow_h", "roadmap", "cycle"),
    "Architecture": _idx("layered", "pillars", "matrix", "concentric", "radial"),
    "Cloud Architecture": _idx("layered", "pillars", "grid_matrix", "honeycomb"),
    "RAG Architecture": _idx("flow_h", "layered", "steps", "cycle"),
    "Agent Architecture": _idx("cycle", "flow_h", "radial", "steps"),
    "Security Architecture": _idx("concentric", "layered", "pillars", "matrix"),
    "Component": _idx("layered", "tree", "honeycomb", "grid_matrix"),
    "Deployment": _idx("layered", "pillars", "swimlane"),
    "Network": _idx("radial", "mindmap", "honeycomb"),
    "Infrastructure": _idx("layered", "pillars", "grid_matrix"),
}
# Anything not listed may use the "analytical/infographic" set.
_DEFAULT_SET = _idx("funnel", "pyramid", "donut", "bars", "matrix", "kpi",
                    "gauge", "concentric", "venn", "roadmap", "ladder", "timeline")


def render_infographic(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    options = KIND_TEMPLATES.get(kind, _DEFAULT_SET)
    ti = rng.choice(options)
    tpl = TEMPLATES[ti]
    pi = rng.randrange(len(PALETTES))
    pal = PALETTES[pi]
    # rotate the palette for extra variety
    shift = rng.randrange(len(pal))
    pal = pal[shift:] + pal[:shift]
    inner = tpl(domain, title, pal, rng)
    uid = format(rng.getrandbits(28), "x")
    grad = (f'<defs><linearGradient id="bn{uid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{pal[0]}"/>'
            f'<stop offset="1" stop-color="{pal[1 % len(pal)]}"/></linearGradient></defs>')
    footer = _txt(PAD, H - 14, _short(domain["name"] + "  \u2022  " + kind, 80), 9.5, MUTED, "start", "500")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'data-tpl="{TEMPLATE_NAMES[ti]}" data-pal="{pi}-{shift}" '
        f'viewBox="0 0 {W} {H}" font-family="Inter, Segoe UI, Arial, sans-serif">'
        f'{_DEFS}{grad}<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>'
        f'<rect x="0" y="0" width="{W}" height="48" rx="14" fill="url(#bn{uid})"/>'
        f'<rect x="0" y="32" width="{W}" height="16" fill="url(#bn{uid})"/>'
        f'{_txt(W/2, 25, _short(title, 92), 14.5, "#ffffff", weight="700")}'
        f'{inner}{footer}</svg>'
    )


def render_named(name: str, items, subject: str = "", pal_index: int = 0,
                 seed: int = 7) -> str:
    """Render a specific template from an explicit list of ``items`` (used by the
    Diagram Studio to turn a prompt/text into a professional diagram)."""
    rng = random.Random(seed)
    if name not in _BY_NAME:
        name = "flow_h"
    ti = _BY_NAME[name]
    items = [str(i).strip() for i in items if str(i).strip()] or ["Item 1", "Item 2", "Item 3"]
    title = (subject or items[0]).strip()
    pseudo = {"name": title, "concepts": [(i, "") for i in items], "_ordered": True,
              "use_cases": [], "best_practices": [], "pitfalls": [], "patterns": [],
              "tools": [], "overview": "", "architecture": ""}
    pi = pal_index % len(PALETTES)
    pal = PALETTES[pi]
    inner = TEMPLATES[ti](pseudo, title, pal, rng)
    uid = format(rng.getrandbits(28), "x")
    grad = (f'<defs><linearGradient id="bn{uid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{pal[0]}"/>'
            f'<stop offset="1" stop-color="{pal[1 % len(pal)]}"/></linearGradient></defs>')
    footer = _txt(PAD, H - 14, _short(title or "Diagram", 80), 9.5, MUTED, "start", "500")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'data-tpl="{name}" data-pal="{pi}" '
        f'viewBox="0 0 {W} {H}" font-family="Inter, Segoe UI, Arial, sans-serif">'
        f'{_DEFS}{grad}<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>'
        f'<rect x="0" y="0" width="{W}" height="48" rx="14" fill="url(#bn{uid})"/>'
        f'<rect x="0" y="32" width="{W}" height="16" fill="url(#bn{uid})"/>'
        f'{_txt(W/2, 25, _short(title, 92), 14.5, "#ffffff", "middle", "700")}'
        f'{inner}{footer}</svg>'
    )
