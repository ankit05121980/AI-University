"""Professional diagram generation in Mermaid, PlantUML, SVG and Draw.io XML.

Diagrams are generated from a domain's architecture, patterns and concepts so
they are topically relevant rather than generic. Source for every diagram is
emitted in one of four formats and stored separately by the exporter.
"""
from __future__ import annotations

import random
from xml.sax.saxutils import escape

from ..models import Diagram

DIAGRAM_KINDS = [
    "Architecture", "Application Flow", "Business Process", "Data Flow",
    "Sequence", "Class", "Component", "Deployment", "Network",
    "Cloud Architecture", "RAG Architecture", "Agent Architecture",
    "Security Architecture", "DevOps Pipeline", "CI/CD Pipeline",
    "Infrastructure", "Knowledge Graph", "Data Lineage", "Capability Map",
    "Operating Model",
]


def _short(name: str, n: int = 18) -> str:
    return name if len(name) <= n else name[: n - 1] + "…"


# --- Mermaid generators ------------------------------------------------------

def _mermaid_architecture(domain: dict, title: str, rng: random.Random) -> str:
    name = domain["name"]
    comps = [c[0] for c in domain["concepts"][:6]]
    lines = ["flowchart TB"]
    lines.append('  subgraph Client["Consumers"]')
    lines.append("    U[Users / Applications]")
    lines.append("    API[API Clients]")
    lines.append("  end")
    lines.append('  subgraph Platform["%s Platform"]' % _short(name, 30))
    lines.append("    GW[Gateway / Orchestrator]")
    for i, c in enumerate(comps):
        lines.append(f"    S{i}[{_short(c, 26)}]")
    lines.append("  end")
    lines.append('  subgraph Data["Data & Storage"]')
    lines.append("    DS[(Primary Store)]")
    lines.append("    VEC[(Vector / Index Store)]")
    lines.append("  end")
    lines.append('  subgraph Ops["Operations & Governance"]')
    lines.append("    OBS[Observability]")
    lines.append("    SEC[Security & Policy]")
    lines.append("  end")
    lines.append("  U --> GW")
    lines.append("  API --> GW")
    for i in range(len(comps)):
        lines.append(f"  GW --> S{i}")
    lines.append("  S0 --> DS")
    lines.append(f"  S{min(1, len(comps)-1)} --> VEC")
    lines.append("  GW -.-> OBS")
    lines.append("  GW -.-> SEC")
    return "\n".join(lines)


def _mermaid_sequence(domain: dict, title: str, rng: random.Random) -> str:
    comps = [c[0] for c in domain["concepts"]]
    a, b = comps[0], comps[1 % len(comps)]
    lines = ["sequenceDiagram", "  autonumber"]
    lines.append("  participant U as User")
    lines.append("  participant G as Gateway")
    lines.append("  participant P as Processor")
    lines.append("  participant D as Data Store")
    lines.append("  U->>G: Submit request")
    lines.append("  G->>G: Validate & authorise")
    lines.append("  G->>P: Dispatch task")
    lines.append("  P->>D: Retrieve context")
    lines.append("  D-->>P: Return records")
    lines.append("  P->>P: Process & reason")
    lines.append("  P-->>G: Result + metadata")
    lines.append("  G-->>U: Response (with provenance)")
    return "\n".join(lines)


def _mermaid_dataflow(domain: dict, title: str, rng: random.Random) -> str:
    lines = ["flowchart LR"]
    lines.append("  SRC[Sources] --> ING[Ingestion]")
    lines.append("  ING --> VAL{Validate}")
    lines.append("  VAL -- ok --> XF[Transform / Enrich]")
    lines.append("  VAL -- reject --> DLQ[(Dead-letter)]")
    lines.append("  XF --> IDX[Index / Embed]")
    lines.append("  IDX --> STORE[(Serving Store)]")
    lines.append("  STORE --> CONS[Consumers]")
    return "\n".join(lines)


def _mermaid_pipeline(domain: dict, title: str, rng: random.Random) -> str:
    lines = ["flowchart LR"]
    stages = ["Commit", "Build", "Test", "Eval Gate", "Package", "Deploy", "Monitor"]
    prev = None
    for i, s in enumerate(stages):
        node = f"S{i}[{s}]"
        lines.append(f"  {node}")
        if prev is not None:
            lines.append(f"  S{i-1} --> S{i}")
        prev = i
    lines.append("  S6 -.->|drift / regression| S0")
    return "\n".join(lines)


def _mermaid_class(domain: dict, title: str, rng: random.Random) -> str:
    name = "".join(w[:1] for w in domain["name"].split())[:4] or "Sys"
    lines = ["classDiagram"]
    lines.append(f"  class {name}Service {{")
    lines.append("    +configure(config)")
    lines.append("    +process(request) Response")
    lines.append("    +evaluate(sample) Metrics")
    lines.append("  }")
    lines.append("  class Repository {")
    lines.append("    +get(id) Entity")
    lines.append("    +put(entity)")
    lines.append("  }")
    lines.append("  class Policy {")
    lines.append("    +authorise(ctx) bool")
    lines.append("  }")
    lines.append(f"  {name}Service --> Repository")
    lines.append(f"  {name}Service --> Policy")
    return "\n".join(lines)


def _mermaid_knowledge_graph(domain: dict, title: str, rng: random.Random) -> str:
    concepts = [c[0] for c in domain["concepts"][:5]]
    lines = ["graph LR"]
    lines.append(f'  D(("{_short(domain["name"], 20)}"))')
    for i, c in enumerate(concepts):
        lines.append(f"  D --- C{i}[{_short(c, 22)}]")
    if len(concepts) >= 3:
        lines.append("  C0 --- C1")
        lines.append("  C1 --- C2")
    return "\n".join(lines)


_MERMAID_BY_KIND = {
    "Sequence": _mermaid_sequence,
    "Application Flow": _mermaid_dataflow,
    "Data Flow": _mermaid_dataflow,
    "Business Process": _mermaid_dataflow,
    "Data Lineage": _mermaid_dataflow,
    "DevOps Pipeline": _mermaid_pipeline,
    "CI/CD Pipeline": _mermaid_pipeline,
    "Class": _mermaid_class,
    "Knowledge Graph": _mermaid_knowledge_graph,
    "Capability Map": _mermaid_knowledge_graph,
}


def _mermaid(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    fn = _MERMAID_BY_KIND.get(kind, _mermaid_architecture)
    return fn(domain, title, rng)


# --- PlantUML ----------------------------------------------------------------

def _plantuml(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    name = domain["name"]
    if kind in ("Sequence",):
        return (
            "@startuml\n"
            f"title {title}\n"
            "actor User\n"
            "participant Gateway\n"
            "participant Processor\n"
            "database Store\n"
            "User -> Gateway : request\n"
            "Gateway -> Processor : dispatch\n"
            "Processor -> Store : retrieve\n"
            "Store --> Processor : context\n"
            "Processor --> Gateway : result\n"
            "Gateway --> User : response\n"
            "@enduml"
        )
    if kind in ("Component", "Deployment", "Infrastructure", "Network"):
        comps = [c[0] for c in domain["concepts"][:5]]
        body = ["@startuml", f"title {title}", "package \"%s Platform\" {" % name]
        for i, c in enumerate(comps):
            body.append(f'  component "{_short(c, 24)}" as C{i}')
        body.append("}")
        body.append('database "Storage" as DB')
        for i in range(len(comps)):
            body.append(f"C{i} --> DB")
        body.append("@enduml")
        return "\n".join(body)
    # default: class diagram
    return (
        "@startuml\n"
        f"title {title}\n"
        "class Service {\n  +process(req)\n  +evaluate(sample)\n}\n"
        "class Repository {\n  +get(id)\n  +put(e)\n}\n"
        "Service --> Repository\n"
        "@enduml"
    )


# --- SVG ---------------------------------------------------------------------

def _svg(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    palette = ["#2563eb", "#7c3aed", "#0891b2", "#059669", "#d97706", "#dc2626"]
    comps = [c[0] for c in domain["concepts"][:5]]
    width, height = 760, 360
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Inter, Arial, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#f8fafc"/>',
        f'<text x="{width//2}" y="34" text-anchor="middle" font-size="20" '
        f'font-weight="700" fill="#0f172a">{escape(_short(title, 56))}</text>',
    ]
    # central node
    cx, cy = width // 2, height // 2 + 10
    parts.append(
        f'<rect x="{cx-90}" y="{cy-28}" width="180" height="56" rx="12" '
        f'fill="#0f172a"/>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="14" '
        f'font-weight="700" fill="#ffffff">{escape(_short(domain["name"], 22))}</text>'
    )
    import math

    n = max(1, len(comps))
    for i, c in enumerate(comps):
        angle = (2 * math.pi * i) / n - math.pi / 2
        bx = cx + int(250 * math.cos(angle))
        by = cy + int(120 * math.sin(angle))
        color = palette[i % len(palette)]
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{bx}" y2="{by}" stroke="#94a3b8" '
            f'stroke-width="2"/>'
        )
        parts.append(
            f'<rect x="{bx-72}" y="{by-22}" width="144" height="44" rx="10" '
            f'fill="#ffffff" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{bx}" y="{by+4}" text-anchor="middle" font-size="11" '
            f'fill="#0f172a">{escape(_short(c, 20))}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


# --- Draw.io XML -------------------------------------------------------------

def _drawio(domain: dict, kind: str, title: str, rng: random.Random) -> str:
    comps = [c[0] for c in domain["concepts"][:5]]
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
    ]
    cells.append(
        '<mxCell id="title" value="%s" style="text;fontSize=16;fontStyle=1" '
        'vertex="1" parent="1"><mxGeometry x="40" y="20" width="600" height="30" '
        'as="geometry"/></mxCell>' % escape(_short(title, 60))
    )
    cells.append(
        '<mxCell id="hub" value="%s" '
        'style="rounded=1;fillColor=#0f172a;fontColor=#ffffff;fontStyle=1" '
        'vertex="1" parent="1"><mxGeometry x="300" y="180" width="160" height="60" '
        'as="geometry"/></mxCell>' % escape(_short(domain["name"], 22))
    )
    y = 80
    for i, c in enumerate(comps):
        cells.append(
            '<mxCell id="n%d" value="%s" '
            'style="rounded=1;fillColor=#e0e7ff;strokeColor=#4338ca" vertex="1" '
            'parent="1"><mxGeometry x="%d" y="%d" width="160" height="50" '
            'as="geometry"/></mxCell>' % (i, escape(_short(c, 24)), 60 + (i % 2) * 540, y)
        )
        cells.append(
            '<mxCell id="e%d" style="edgeStyle=orthogonalEdgeStyle" edge="1" '
            'parent="1" source="hub" target="n%d"><mxGeometry relative="1" '
            'as="geometry"/></mxCell>' % (i, i)
        )
        y += 90
    inner = "\n        ".join(cells)
    return (
        '<mxfile host="ai-university">\n'
        '  <diagram name="%s">\n'
        "    <mxGraphModel dx=\"800\" dy=\"600\" grid=\"1\" gridSize=\"10\">\n"
        "      <root>\n        %s\n      </root>\n"
        "    </mxGraphModel>\n"
        "  </diagram>\n"
        "</mxfile>" % (escape(_short(kind, 30)), inner)
    )


_FORMAT_DISPATCH = {
    "mermaid": _mermaid,
    "plantuml": _plantuml,
    "svg": _svg,
    "drawio": _drawio,
}

# Which formats are valid/most natural for each kind.
_KIND_FORMATS = {
    "Sequence": ["mermaid", "plantuml"],
    "Class": ["mermaid", "plantuml"],
    "Component": ["plantuml", "mermaid"],
    "Deployment": ["plantuml", "drawio"],
    "Network": ["drawio", "plantuml"],
    "Knowledge Graph": ["mermaid", "svg"],
    "Capability Map": ["svg", "mermaid"],
    "Operating Model": ["svg", "drawio"],
    "Infrastructure": ["drawio", "plantuml"],
}


def make_diagram(domain: dict, kind: str, title: str, rng: random.Random,
                 fmt: str | None = None) -> Diagram:
    if fmt is None:
        fmt = rng.choice(_KIND_FORMATS.get(kind, ["mermaid", "svg", "plantuml", "drawio"]))
    source = _FORMAT_DISPATCH[fmt](domain, kind, title, rng)
    caption = (
        f"Figure: {kind} view for {domain['name']}. "
        f"This diagram illustrates the principal components and their interactions "
        f"as discussed in the surrounding section."
    )
    return Diagram(title=title, kind=kind, fmt=fmt, source=source, caption=caption)
