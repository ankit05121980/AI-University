"""Professional diagram generation in Mermaid, PlantUML, SVG and Draw.io XML.

Every diagram carries two things:

* ``source`` — the editable source in one of four formats (Mermaid, PlantUML,
  SVG, Draw.io XML), stored separately by the exporter; and
* ``render_svg`` — a self-contained, dependency-free SVG rendering used by the
  web viewer, the HTML export and (where possible) the PDF, so diagrams are
  always visible without any external renderer.
"""
from __future__ import annotations

import math
import random
from xml.sax.saxutils import escape

from ..models import Diagram
from .infographics import render_infographic

DIAGRAM_KINDS = [
    "Architecture", "Application Flow", "Business Process", "Data Flow",
    "Sequence", "Class", "Component", "Deployment", "Network",
    "Cloud Architecture", "RAG Architecture", "Agent Architecture",
    "Security Architecture", "DevOps Pipeline", "CI/CD Pipeline",
    "Infrastructure", "Knowledge Graph", "Data Lineage", "Capability Map",
    "Operating Model",
]

PALETTE = ["#4338ca", "#7c3aed", "#0891b2", "#059669", "#d97706", "#dc2626", "#0ea5e9"]


def _short(name: str, n: int = 18) -> str:
    return name if len(name) <= n else name[: n - 1] + "\u2026"


# ===========================================================================
# Mermaid / PlantUML / Draw.io / SVG source generators (editable source files)
# ===========================================================================

def _mermaid_architecture(domain: dict, title: str, rng: random.Random) -> str:
    name = domain["name"]
    comps = [c[0] for c in domain["concepts"][:6]]
    lines = ["flowchart TB", '  subgraph Client["Consumers"]', "    U[Users / Applications]",
             "    API[API Clients]", "  end", '  subgraph Platform["%s Platform"]' % _short(name, 30),
             "    GW[Gateway / Orchestrator]"]
    for i, c in enumerate(comps):
        lines.append(f"    S{i}[{_short(c, 26)}]")
    lines += ["  end", '  subgraph Data["Data & Storage"]', "    DS[(Primary Store)]",
              "    VEC[(Vector / Index Store)]", "  end",
              '  subgraph Ops["Operations & Governance"]', "    OBS[Observability]",
              "    SEC[Security & Policy]", "  end", "  U --> GW", "  API --> GW"]
    for i in range(len(comps)):
        lines.append(f"  GW --> S{i}")
    lines += ["  S0 --> DS", f"  S{min(1, len(comps)-1)} --> VEC", "  GW -.-> OBS", "  GW -.-> SEC"]
    return "\n".join(lines)


def _mermaid_sequence(domain: dict, title: str, rng: random.Random) -> str:
    return "\n".join([
        "sequenceDiagram", "  autonumber", "  participant U as User", "  participant G as Gateway",
        "  participant P as Processor", "  participant D as Data Store",
        "  U->>G: Submit request", "  G->>G: Validate & authorise", "  G->>P: Dispatch task",
        "  P->>D: Retrieve context", "  D-->>P: Return records", "  P->>P: Process & reason",
        "  P-->>G: Result + metadata", "  G-->>U: Response (with provenance)",
    ])


def _mermaid_dataflow(domain: dict, title: str, rng: random.Random) -> str:
    return "\n".join([
        "flowchart LR", "  SRC[Sources] --> ING[Ingestion]", "  ING --> VAL{Validate}",
        "  VAL -- ok --> XF[Transform / Enrich]", "  VAL -- reject --> DLQ[(Dead-letter)]",
        "  XF --> IDX[Index / Embed]", "  IDX --> STORE[(Serving Store)]", "  STORE --> CONS[Consumers]",
    ])


def _mermaid_pipeline(domain: dict, title: str, rng: random.Random) -> str:
    stages = ["Commit", "Build", "Test", "Eval Gate", "Package", "Deploy", "Monitor"]
    lines = ["flowchart LR"]
    for i, s in enumerate(stages):
        lines.append(f"  S{i}[{s}]")
        if i:
            lines.append(f"  S{i-1} --> S{i}")
    lines.append("  S6 -.->|drift / regression| S0")
    return "\n".join(lines)


def _mermaid_class(domain: dict, title: str, rng: random.Random) -> str:
    name = "".join(w[:1] for w in domain["name"].split())[:4] or "Sys"
    return "\n".join([
        "classDiagram", f"  class {name}Service {{", "    +configure(config)",
        "    +process(request) Response", "    +evaluate(sample) Metrics", "  }",
        "  class Repository {", "    +get(id) Entity", "    +put(entity)", "  }",
        "  class Policy {", "    +authorise(ctx) bool", "  }",
        f"  {name}Service --> Repository", f"  {name}Service --> Policy",
    ])


def _mermaid_knowledge_graph(domain: dict, title: str, rng: random.Random) -> str:
    concepts = [c[0] for c in domain["concepts"][:5]]
    lines = ["graph LR", f'  D(("{_short(domain["name"], 20)}"))']
    for i, c in enumerate(concepts):
        lines.append(f"  D --- C{i}[{_short(c, 22)}]")
    if len(concepts) >= 3:
        lines += ["  C0 --- C1", "  C1 --- C2"]
    return "\n".join(lines)


_MERMAID_BY_KIND = {
    "Sequence": _mermaid_sequence, "Application Flow": _mermaid_dataflow,
    "Data Flow": _mermaid_dataflow, "Business Process": _mermaid_dataflow,
    "Data Lineage": _mermaid_dataflow, "DevOps Pipeline": _mermaid_pipeline,
    "CI/CD Pipeline": _mermaid_pipeline, "Class": _mermaid_class,
    "Knowledge Graph": _mermaid_knowledge_graph, "Capability Map": _mermaid_knowledge_graph,
}


def _mermaid(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    return _MERMAID_BY_KIND.get(kind, _mermaid_architecture)(domain, title, rng)


def _plantuml(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    name = domain["name"]
    if kind == "Sequence":
        return ("@startuml\n" f"title {title}\n" "actor User\nparticipant Gateway\n"
                "participant Processor\ndatabase Store\n"
                "User -> Gateway : request\nGateway -> Processor : dispatch\n"
                "Processor -> Store : retrieve\nStore --> Processor : context\n"
                "Processor --> Gateway : result\nGateway --> User : response\n@enduml")
    if kind in ("Component", "Deployment", "Infrastructure", "Network"):
        comps = [c[0] for c in domain["concepts"][:5]]
        body = ["@startuml", f"title {title}", 'package "%s Platform" {' % name]
        for i, c in enumerate(comps):
            body.append(f'  component "{_short(c, 24)}" as C{i}')
        body.append("}")
        body.append('database "Storage" as DB')
        for i in range(len(comps)):
            body.append(f"C{i} --> DB")
        body.append("@enduml")
        return "\n".join(body)
    return ("@startuml\n" f"title {title}\n"
            "class Service {\n  +process(req)\n  +evaluate(sample)\n}\n"
            "class Repository {\n  +get(id)\n  +put(e)\n}\nService --> Repository\n@enduml")


def _drawio(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    comps = [c[0] for c in domain["concepts"][:5]]
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>',
             '<mxCell id="title" value="%s" style="text;fontSize=16;fontStyle=1" vertex="1" '
             'parent="1"><mxGeometry x="40" y="20" width="600" height="30" as="geometry"/></mxCell>'
             % escape(_short(title, 60)),
             '<mxCell id="hub" value="%s" style="rounded=1;fillColor=#0f172a;fontColor=#ffffff;'
             'fontStyle=1" vertex="1" parent="1"><mxGeometry x="300" y="180" width="160" height="60" '
             'as="geometry"/></mxCell>' % escape(_short(domain["name"], 22))]
    y = 80
    for i, c in enumerate(comps):
        cells.append('<mxCell id="n%d" value="%s" style="rounded=1;fillColor=#e0e7ff;'
                     'strokeColor=#4338ca" vertex="1" parent="1"><mxGeometry x="%d" y="%d" '
                     'width="160" height="50" as="geometry"/></mxCell>'
                     % (i, escape(_short(c, 24)), 60 + (i % 2) * 540, y))
        cells.append('<mxCell id="e%d" style="edgeStyle=orthogonalEdgeStyle" edge="1" parent="1" '
                     'source="hub" target="n%d"><mxGeometry relative="1" as="geometry"/></mxCell>' % (i, i))
        y += 90
    inner = "\n        ".join(cells)
    return ('<mxfile host="ai-university">\n  <diagram name="%s">\n'
            '    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10">\n      <root>\n'
            "        %s\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>"
            % (escape(_short(kind, 30)), inner))


def _svg_source(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    # The "svg" *source* format is simply the rendered infographic itself.
    return render_infographic(domain, kind, title, rng)


_FORMAT_DISPATCH = {"mermaid": _mermaid, "plantuml": _plantuml,
                    "svg": _svg_source, "drawio": _drawio}

_KIND_FORMATS = {
    "Sequence": ["mermaid", "plantuml"], "Class": ["mermaid", "plantuml"],
    "Component": ["plantuml", "mermaid"], "Deployment": ["plantuml", "drawio"],
    "Network": ["drawio", "plantuml"], "Knowledge Graph": ["mermaid", "svg"],
    "Capability Map": ["svg", "mermaid"], "Operating Model": ["svg", "drawio"],
    "Infrastructure": ["drawio", "plantuml"],
}


# ===========================================================================
# Self-contained SVG renderer (always available; used by viewers)
# ===========================================================================

_W, _H = 760, 380
_DEFS = (
    '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" '
    'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 z" fill="#94a3b8"/></marker>'
    '<marker id="arrowA" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" '
    'markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 z" fill="#4338ca"/></marker></defs>'
)


def _svg_open(title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_W}" height="{_H}" '
        f'viewBox="0 0 {_W} {_H}" font-family="Inter, Segoe UI, Arial, sans-serif">',
        _DEFS,
        f'<rect width="{_W}" height="{_H}" rx="12" fill="#f8fafc"/>',
        f'<text x="{_W//2}" y="30" text-anchor="middle" font-size="17" font-weight="700" '
        f'fill="#0f172a">{escape(_short(title, 60))}</text>',
    ]


def _box(x, y, w, h, label, fill="#ffffff", stroke="#4338ca", fg="#0f172a", fs=12, sub=None):
    cx, cy = x + w / 2, y + h / 2
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="2"/>']
    label = _short(label, int(w / (fs * 0.56)))
    ty = cy + (fs * 0.34) if not sub else cy - 2
    out.append(f'<text x="{cx}" y="{ty}" text-anchor="middle" font-size="{fs}" font-weight="600" '
               f'fill="{fg}">{escape(label)}</text>')
    if sub:
        out.append(f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-size="9.5" '
                   f'fill="#64748b">{escape(_short(sub, 22))}</text>')
    return "".join(out)


def _arrow(x1, y1, x2, y2, accent=False, label=None):
    mk = "arrowA" if accent else "arrow"
    col = "#4338ca" if accent else "#94a3b8"
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2" '
           f'marker-end="url(#{mk})"/>']
    if label:
        out.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2 - 6}" text-anchor="middle" font-size="9" '
                   f'fill="#64748b">{escape(label)}</text>')
    return "".join(out)


_FLOW_STAGES = {
    "RAG Architecture": ["Query", "Embed", "Retrieve", "Re-rank", "Generate", "Answer"],
    "Agent Architecture": ["Goal", "Plan", "Tool Call", "Observe", "Reflect", "Act"],
    "Data Flow": ["Sources", "Ingest", "Validate", "Transform", "Index", "Serve"],
    "Application Flow": ["Request", "Auth", "Route", "Process", "Persist", "Respond"],
    "Business Process": ["Intake", "Assess", "Decide", "Execute", "Review", "Close"],
    "Data Lineage": ["Source", "Raw", "Curated", "Feature", "Model", "Serving"],
    "DevOps Pipeline": ["Commit", "Build", "Test", "Scan", "Deploy", "Monitor"],
    "CI/CD Pipeline": ["Commit", "Build", "Eval Gate", "Package", "Deploy", "Monitor"],
}


def _render_flow(domain, kind, title, rng):
    stages = _FLOW_STAGES.get(kind)
    if not stages:
        stages = ["Input"] + [_short(c[0], 14) for c in domain["concepts"][:4]] + ["Output"]
    stages = stages[:6]
    parts = _svg_open(title)
    n = len(stages)
    bw, bh, gap = 104, 60, (_W - 80 - n * 104) / max(1, n - 1)
    y = _H / 2 - bh / 2 + 6
    xs = [40 + i * (bw + gap) for i in range(n)]
    for i, s in enumerate(stages):
        parts.append(_box(xs[i], y, bw, bh, s, fill="#ffffff",
                          stroke=PALETTE[i % len(PALETTE)]))
        if i:
            parts.append(_arrow(xs[i - 1] + bw, y + bh / 2, xs[i], y + bh / 2, accent=True))
    # feedback loop
    parts.append(f'<path d="M{xs[-1]+bw/2},{y+bh} q0,46 -{(xs[-1]-xs[0])/2},46 '
                 f'q-{(xs[-1]-xs[0])/2},0 -{(xs[-1]-xs[0])/2},-46" fill="none" stroke="#cbd5e1" '
                 f'stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#arrow)"/>')
    parts.append(f'<text x="{_W/2}" y="{y+bh+62}" text-anchor="middle" font-size="9.5" '
                 f'fill="#94a3b8">feedback / monitoring loop</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _render_layered(domain, kind, title, rng):
    name = domain["name"]
    comps = [c[0] for c in domain["concepts"][:4]]
    parts = _svg_open(title)
    layers = [
        ("Consumers", ["Users / Apps", "API Clients"], "#eef2ff"),
        (f"{_short(name,22)} Platform", ["Gateway"] + comps, "#f5f3ff"),
        ("Data & Operations", ["Primary Store", "Vector Index", "Observability", "Security"], "#ecfeff"),
    ]
    ly = 48
    lh = 96
    centers = []
    for li, (lname, boxes, bg) in enumerate(layers):
        parts.append(f'<rect x="30" y="{ly}" width="{_W-60}" height="{lh}" rx="12" fill="{bg}" '
                     f'stroke="#e2e8f0"/>')
        parts.append(f'<text x="44" y="{ly+18}" font-size="11" font-weight="700" '
                     f'fill="#475569">{escape(lname)}</text>')
        m = len(boxes)
        bw = min(150, (_W - 90 - (m - 1) * 14) / m)
        bx = 44
        rowc = []
        for bi, b in enumerate(boxes):
            x = bx + bi * (bw + 14)
            parts.append(_box(x, ly + 30, bw, 48, b, fill="#ffffff",
                              stroke=PALETTE[(li + bi) % len(PALETTE)], fs=11))
            rowc.append((x + bw / 2, ly + 30, ly + 30 + 48))
        centers.append(rowc)
        ly += lh + 22
    # connect layer 0 -> 1 -> 2 (center arrows)
    for a, b in ((0, 1), (1, 2)):
        x1 = centers[a][0][0]
        x2 = centers[b][0][0]
        parts.append(_arrow(_W / 2, centers[a][0][2], _W / 2, centers[b][0][1], accent=True))
    parts.append("</svg>")
    return "\n".join(parts)


def _render_sequence(domain, kind, title, rng):
    actors = ["User", "Gateway", "Processor", "Data Store"]
    msgs = [(0, 1, "request"), (1, 1, "validate"), (1, 2, "dispatch"), (2, 3, "retrieve"),
            (3, 2, "records"), (2, 1, "result"), (1, 0, "response")]
    parts = _svg_open(title)
    n = len(actors)
    xs = [80 + i * ((_W - 160) / (n - 1)) for i in range(n)]
    top = 56
    bottom = _H - 30
    for i, a in enumerate(actors):
        parts.append(_box(xs[i] - 60, top, 120, 34, a, fill="#eef2ff", stroke="#4338ca", fs=11))
        parts.append(f'<line x1="{xs[i]}" y1="{top+34}" x2="{xs[i]}" y2="{bottom}" '
                     f'stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4"/>')
    y = top + 64
    for (a, b, label) in msgs:
        if a == b:
            parts.append(f'<path d="M{xs[a]},{y} h34 v18 h-34" fill="none" stroke="#4338ca" '
                         f'stroke-width="1.8" marker-end="url(#arrowA)"/>')
            parts.append(f'<text x="{xs[a]+40}" y="{y+2}" font-size="9.5" fill="#64748b">{escape(label)}</text>')
            y += 34
        else:
            parts.append(_arrow(xs[a], y, xs[b], y, accent=True, label=label))
            y += 30
    parts.append("</svg>")
    return "\n".join(parts)


def _render_radial(domain, kind, title, rng):
    concepts = [c[0] for c in domain["concepts"][:6]]
    parts = _svg_open(title)
    cx, cy = _W / 2, _H / 2 + 8
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="#0f172a"/>')
    parts.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="12" font-weight="700" '
                 f'fill="#ffffff">{escape(_short(domain["name"], 14))}</text>')
    n = max(1, len(concepts))
    for i, c in enumerate(concepts):
        ang = (2 * math.pi * i) / n - math.pi / 2
        bx = cx + 250 * math.cos(ang)
        by = cy + 118 * math.sin(ang)
        parts.append(_arrow(cx + 46 * math.cos(ang), cy + 46 * math.sin(ang),
                            bx - 24 * math.cos(ang), by - 12 * math.sin(ang)))
        parts.append(_box(bx - 74, by - 22, 148, 44, c, fill="#ffffff",
                          stroke=PALETTE[i % len(PALETTE)], fs=11))
    parts.append("</svg>")
    return "\n".join(parts)


_LAYERED_KINDS = {"Architecture", "Component", "Deployment", "Cloud Architecture",
                  "Security Architecture", "Infrastructure", "Network"}
_RADIAL_KINDS = {"Knowledge Graph", "Capability Map", "Operating Model", "Class"}


def render_diagram_svg(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    if kind == "Sequence":
        return _render_sequence(domain, kind, title, rng)
    if kind in _RADIAL_KINDS:
        return _render_radial(domain, kind, title, rng)
    if kind in _LAYERED_KINDS:
        return _render_layered(domain, kind, title, rng)
    return _render_flow(domain, kind, title, rng)


# ===========================================================================

def make_diagram(domain: dict, kind: str, title: str, rng: random.Random,
                 fmt: str | None = None) -> Diagram:
    if fmt is None:
        fmt = rng.choice(_KIND_FORMATS.get(kind, ["mermaid", "svg", "plantuml", "drawio"]))
    source = _FORMAT_DISPATCH[fmt](domain, kind, title, rng)
    render_svg = source if fmt == "svg" else render_infographic(domain, kind, title, rng)
    caption = (
        f"Figure: {kind} view for {domain['name']}. "
        f"This diagram illustrates the principal components and their interactions "
        f"as discussed in the surrounding section."
    )
    return Diagram(title=title, kind=kind, fmt=fmt, source=source, caption=caption,
                   render_svg=render_svg)
