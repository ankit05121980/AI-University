"""Prose composition.

Composes substantive, varied technical prose from the structured domain
knowledge. The goal is enterprise-grade explanatory writing - definitions,
rationale, trade-offs, architecture and operational guidance - rather than
filler. Variety is achieved through large pools of sentence frames seeded
deterministically per chapter, and content is anchored to the specific
concept, patterns, tools, use cases and references of each domain.
"""
from __future__ import annotations

import random

# --- text helpers ------------------------------------------------------------

def _clean(text: str) -> str:
    """Strip surrounding whitespace and a single trailing period."""
    t = text.strip()
    return t[:-1] if t.endswith(".") else t


def _desc_low(desc: str) -> str:
    d = _clean(desc)
    return (d[0].lower() + d[1:]) if d else d


def _para(*sentences: str) -> str:
    return " ".join(s.strip() for s in sentences if s and s.strip()).strip()


def _sentences(rng: random.Random, frames: list[str], **kw) -> str:
    return rng.choice(frames).format(**kw)


# --- Sentence frame pools ----------------------------------------------------

_DEF_FRAMES = [
    "{topic} refers to {desc_low}.",
    "At its core, {topic} concerns {desc_low}.",
    "We define {topic} as {desc_low}.",
    "In practical terms, {topic} is best understood as {desc_low}.",
    "{topic} can be characterised as {desc_low}.",
    "Formally, {topic} addresses {desc_low}.",
]

_IMPORTANCE_FRAMES = [
    "Understanding this matters because {name} systems succeed or fail on exactly these decisions.",
    "Teams that master this consistently ship more reliable {name} systems at lower cost.",
    "Getting this right early prevents expensive rework once a {name} system reaches scale.",
    "This concept recurs throughout the {name} lifecycle, from design to operations.",
    "Neglecting it is one of the most common reasons {name} initiatives stall in production.",
    "It is foundational: later capabilities in {name} are built directly on top of it.",
]

_ELABORATION_FRAMES = [
    "In an enterprise setting, this translates into concrete requirements: clear interfaces, measurable quality, and controls that satisfy security and governance.",
    "The practical implication is that design choices here ripple through latency, cost and maintainability for the lifetime of the system.",
    "What distinguishes a production-grade approach from a prototype is the discipline of measurement: every claim is backed by an evaluation rather than intuition.",
    "Seasoned practitioners treat this as a systems problem, co-designing data, models and operations rather than optimising any one in isolation.",
    "The right abstraction here pays compounding dividends, because downstream components depend on its guarantees.",
    "It helps to separate the conceptual model from its implementation: the former guides reasoning, the latter must contend with real-world constraints.",
]

_MECHANICS_FRAMES = [
    "Mechanically, the behaviour emerges from a few interacting parts that are simpler than the whole they produce.",
    "The underlying mechanism is best appreciated by tracing a single request from input to output and noting where state is created and consumed.",
    "Beneath the abstraction lies a concrete process whose steps can each be measured, tested and optimised independently.",
    "It pays to understand the mechanism rather than treat it as a black box, because most production incidents are explained by one of its steps misbehaving.",
]

_TRADEOFF_FRAMES = [
    "There is an inherent trade-off between fidelity and cost, and the correct balance depends on the use case and its tolerance for error.",
    "As with most architectural decisions, the choice is rarely binary; the skill lies in quantifying the trade-offs and choosing deliberately.",
    "Latency, accuracy and cost form a tension triangle: improving one typically pressures the others, so explicit budgets are essential.",
    "Simplicity is a feature. The simplest design that meets the requirement should be the default, with complexity added only when measurement justifies it.",
    "Every added component buys capability at the price of operational surface area, and that bargain should be made consciously.",
]

_WHEN_FRAMES = [
    "It is worth being explicit about when to apply this and when to reach for something simpler.",
    "Knowing when not to use a technique is as valuable as knowing how to use it.",
    "The decision of whether to adopt this should be driven by requirements, not by novelty.",
]

_ARCH_INTRO = [
    "From an architectural standpoint, {topic} sits at the intersection of data, models and operations.",
    "The reference architecture for {topic} separates concerns into clearly bounded components with explicit contracts.",
    "A robust architecture for {topic} is layered so each part can evolve independently without destabilising the whole.",
]

_EXAMPLE_INTRO = [
    "Consider a concrete scenario.",
    "To ground the discussion, walk through a representative example.",
    "A worked example clarifies how these ideas behave in practice.",
]


# --- Section composers -------------------------------------------------------

def compose_intro(domain: dict, topic: str, desc: str, rng: random.Random) -> str:
    name = domain["name"]
    p1 = _para(
        _sentences(rng, _DEF_FRAMES, topic=topic, desc_low=_desc_low(desc)),
        _sentences(rng, _IMPORTANCE_FRAMES, name=name),
        rng.choice(_ELABORATION_FRAMES),
    )
    p2 = _para(
        f"This chapter builds intuition first, then formalises the ideas, derives an "
        f"architecture, and finishes with code, exercises and review questions so the "
        f"material transfers directly to your own {name} work.",
        "Read it actively: pause at each diagram, reproduce the code, and attempt the "
        "exercises before consulting the answers.",
    )
    return p1 + "\n\n" + p2


def compose_theory(domain: dict, topic: str, desc: str, rng: random.Random,
                   related: list[tuple[str, str]]) -> str:
    name = domain["name"]
    paras: list[str] = []

    paras.append(_para(
        _sentences(rng, _DEF_FRAMES, topic=topic, desc_low=_desc_low(desc)),
        rng.choice(_ELABORATION_FRAMES),
        rng.choice(_MECHANICS_FRAMES),
    ))

    overview = domain.get("overview", "")
    overview_sentence = overview.split(". ")[0].strip()
    if overview_sentence and not overview_sentence.endswith("."):
        overview_sentence += "."
    paras.append(_para(
        f"To place this in context, recall the broader picture: {overview_sentence}",
        f"Within that picture, {topic.lower()} is one of the load-bearing ideas - the kind "
        f"that, when understood deeply, makes the rest of {name} fall into place.",
        _sentences(rng, _IMPORTANCE_FRAMES, name=name),
    ))

    for rtopic, rdesc in related[:2]:
        paras.append(_para(
            f"{topic} cannot be understood in isolation from {rtopic.lower()}.",
            f"Recall that {rtopic.lower()} concerns {_desc_low(rdesc)}.",
            "The two interact directly: decisions in one constrain the design space of the "
            "other, which is why mature teams reason about them together rather than "
            "sequentially.",
            rng.choice(_TRADEOFF_FRAMES),
        ))

    patterns = domain.get("patterns", [])
    if patterns:
        chosen = rng.sample(patterns, min(2, len(patterns)))
        second = ("A complementary pattern, " + chosen[1].lower() + ", addresses a related "
                  "concern and is often deployed alongside it." if len(chosen) > 1 else "")
        paras.append(_para(
            f"Several established patterns apply directly to {topic.lower()}.",
            "The first, " + chosen[0].lower() + ", is widely adopted because it makes the "
            "system's behaviour predictable and observable.",
            second,
            "Patterns are not dogma; they are distilled experience that shortcuts the search "
            "for a sound design, and each carries assumptions worth checking against your "
            "context.",
        ))

    paras.append(_para(
        rng.choice(_WHEN_FRAMES),
        f"In a small prototype, shortcuts around {topic.lower()} are invisible; in a "
        f"production {name} system serving real traffic, they surface as incidents, cost "
        "overruns or compliance gaps.",
        rng.choice(_TRADEOFF_FRAMES),
        "The remainder of this chapter turns these principles into an architecture, code "
        "and a checklist you can apply immediately.",
    ))
    return "\n\n".join(p for p in paras if p)


def compose_architecture(domain: dict, topic: str, rng: random.Random) -> str:
    name = domain["name"]
    arch = domain.get("architecture", "")
    concepts = [c[0] for c in domain.get("concepts", [])][:5]
    paras = []
    paras.append(_para(
        _sentences(rng, _ARCH_INTRO, topic=topic),
        arch,
    ))
    if concepts:
        comp_list = ", ".join(c.lower() for c in concepts[:-1]) + f" and {concepts[-1].lower()}"
        paras.append(_para(
            f"Concretely, the principal building blocks include {comp_list}.",
            "Each is a replaceable component behind a stable interface, so the team can "
            "upgrade an implementation - a model, an index, a policy engine - without "
            "rewriting its neighbours.",
            "The contracts between components are where reliability is won or lost, so they "
            "are specified explicitly and tested in isolation.",
        ))
    paras.append(_para(
        "The diagram accompanying this section makes the data and control flow explicit.",
        "Requests enter through a well-defined boundary where they are authenticated and "
        "validated; only then are they dispatched to the components that perform the work.",
        "This boundary is also where rate limiting, quota enforcement and audit logging "
        "live, keeping cross-cutting concerns out of the core logic and in one auditable "
        "place.",
    ))
    paras.append(_para(
        "Two qualities deserve emphasis.",
        "First, observability is designed in, not bolted on: every component emits structured "
        "telemetry so that failures can be localised in minutes rather than hours.",
        f"Second, the architecture is evolvable - components communicate through stable "
        f"contracts so that any single part of the {name} system can be replaced without a "
        "rewrite.",
        rng.choice(_TRADEOFF_FRAMES),
    ))
    return "\n\n".join(paras)


def compose_example(domain: dict, topic: str, rng: random.Random) -> str:
    name = domain["name"]
    use_cases = domain.get("use_cases", [])
    uc = rng.choice(use_cases) if use_cases else (name, "a representative workload")
    industry, scenario = uc
    paras = []
    paras.append(_para(
        rng.choice(_EXAMPLE_INTRO),
        f"A {industry.lower()} organisation needs {_desc_low(scenario)}.",
        f"They decide to apply {topic.lower()} as part of their {name} solution, but wisely "
        "treat it as a hypothesis to be validated rather than a foregone conclusion.",
    ))
    paras.append(_para(
        "The team begins by stating the objective precisely and defining how success will "
        "be measured before writing any code.",
        "They establish a small but representative evaluation set, agree on acceptance "
        "thresholds, and only then prototype the simplest design that could work.",
        "Early measurement reveals which assumptions hold and which must be revised, saving "
        "weeks of misdirected effort and surfacing edge cases while they are still cheap to "
        "fix.",
    ))
    paras.append(_para(
        "As the prototype matures into a service, the team hardens it: adding input "
        "validation, error handling, caching where it pays off, and monitoring that ties "
        "back to the original success metric.",
        "They document each significant decision in an architecture decision record so that "
        "future maintainers understand not just what was built but why.",
    ))
    paras.append(_para(
        "The outcome is instructive.",
        "The system that reaches production is not the most sophisticated design the team "
        "considered, but the one whose behaviour they could measure, explain and operate.",
        f"This is the recurring lesson of {name}: durable value comes from the whole system, "
        "not from any single clever component.",
    ))
    return "\n\n".join(paras)


def compose_deep_dive(domain: dict, topic: str, rng: random.Random,
                      related: list[tuple[str, str]]) -> str:
    name = domain["name"]
    tools = domain.get("tools", [])
    refs = domain.get("references", [])
    paras = []
    paras.append(_para(
        f"Having established the essentials, we now go deeper into {topic.lower()}.",
        rng.choice(_MECHANICS_FRAMES),
        "The distinctions in this section are the ones that separate a working demo from a "
        "system that holds up under adversarial inputs, scale and the passage of time.",
    ))
    paras.append(_para(
        "Consider the principal variants and how to choose between them.",
        "Each variant optimises for a different point in the design space - some for latency, "
        "some for accuracy, some for cost or operability - and the correct choice follows "
        "from explicit requirements rather than from defaults.",
        rng.choice(_TRADEOFF_FRAMES),
    ))
    if tools:
        tool_list = ", ".join(tools[:4])
        paras.append(_para(
            f"In practice this is supported by a mature tooling ecosystem, including {tool_list}.",
            "Tools accelerate the work but do not substitute for understanding: the same "
            "principles apply whichever implementation you select, and the ability to reason "
            "from first principles is what lets you debug when a tool behaves unexpectedly.",
        ))
    if related:
        rtopic, rdesc = related[0]
        paras.append(_para(
            f"A frequent source of subtle bugs is the interaction with {rtopic.lower()}.",
            f"Because {rtopic.lower()} concerns {_desc_low(rdesc)}, changes there can silently "
            f"alter the behaviour analysed here.",
            "The remedy is contract tests at the boundary and end-to-end evaluations that "
            "exercise the interaction explicitly.",
        ))
    paras.append(_para(
        "Finally, attend to edge cases and degradation.",
        "Define what the system should do under partial failure, unexpected inputs and load "
        "spikes, and make that behaviour explicit and tested rather than emergent.",
        "Graceful degradation - returning a safe, useful result when the ideal one is "
        "unavailable - is a hallmark of mature engineering.",
    ))
    if refs:
        paras.append(_para(
            f"For deeper study, the literature offers authoritative treatments such as "
            f"{refs[0]}" + (f" and {refs[1]}" if len(refs) > 1 else "") + ".",
            "These primary sources reward careful reading and ground the practical guidance "
            "above in established results.",
        ))
    return "\n\n".join(paras)


def compose_governance_notes(domain: dict, topic: str, rng: random.Random) -> str:
    name = domain["name"]
    paras = []
    paras.append(_para(
        f"No discussion of {topic.lower()} is complete without its governance, security and "
        f"cost dimensions, which are too often deferred until they become emergencies.",
        "Treating them as first-class concerns from the outset is both cheaper and safer.",
    ))
    paras.append(_para(
        "**Governance.** Classify the risk of this capability, document its intended and "
        "out-of-scope uses, and ensure decisions are traceable to satisfy internal policy "
        "and external regulation such as the NIST AI RMF, ISO/IEC 42001 and the EU AI Act.",
        "**Security.** Treat all external input as untrusted, validate outputs before acting "
        "on them, apply least privilege to any tools or data access, and map controls to the "
        "OWASP LLM Top 10 and MITRE ATLAS.",
    ))
    paras.append(_para(
        "**Cost and sustainability.** Establish explicit budgets for compute, tokens and "
        "latency, attribute spend to owners, and revisit the economics as usage scales - a "
        "design that is affordable at pilot scale can become untenable at production volume.",
        "Building these reflexes into everyday engineering is what allows a "
        f"{name} system to be not only capable but also trustworthy and economically sound.",
    ))
    return "\n\n".join(paras)


def compose_use_cases(domain: dict, rng: random.Random) -> str:
    use_cases = domain.get("use_cases", [])
    paras = ["Across industries, the ideas in this chapter recur in recognisable ways. The "
             "following vignettes show how different sectors apply them and what they have "
             "in common."]
    for industry, scenario in use_cases:
        paras.append(_para(
            f"**{industry}.** {scenario}",
            "The common thread is that value comes not from the model alone but from the "
            "surrounding system - data quality, evaluation, integration and operations - "
            "which is precisely where most of the engineering effort belongs.",
        ))
    return "\n\n".join(paras)


def compose_best_practices(domain: dict, topic: str, rng: random.Random) -> str:
    practices = domain.get("best_practices", [])
    lead = _para(
        f"The following practices consistently separate successful {domain['name']} efforts "
        f"from struggling ones. They are deliberately concrete so they can be adopted as "
        f"checklist items in design and code review."
    )
    bullets = "\n".join(f"- {p}" for p in practices)
    tail = _para(
        "None of these are exotic; they are the unglamorous disciplines that compound into "
        "reliability. The cost of adopting them is small compared with the cost of the "
        "incidents they prevent, and they become second nature with practice."
    )
    return lead + "\n\n" + bullets + "\n\n" + tail


def compose_pitfalls(domain: dict, topic: str, rng: random.Random) -> str:
    pitfalls = domain.get("pitfalls", [])
    lead = _para(
        "Equally instructive are the failure modes that recur in practice. Each pitfall "
        "below has a clear early warning sign and a known remedy, so treat them as a "
        "diagnostic checklist when something feels wrong:"
    )
    bullets = "\n".join(f"- {p}" for p in pitfalls)
    tail = _para(
        "The pattern is consistent: most failures stem from skipping measurement, conflating "
        "prototype and production standards, or deferring cross-cutting concerns such as "
        "security and cost until they become emergencies. Naming these traps in advance is "
        "the cheapest way to avoid them."
    )
    return lead + "\n\n" + bullets + "\n\n" + tail


def compose_exercises(domain: dict, topic: str, rng: random.Random) -> str:
    name = domain["name"]
    exercises = [
        f"Explain {topic.lower()} to a colleague unfamiliar with {name}, using a concrete "
        f"example from your own domain.",
        f"Sketch a reference architecture that incorporates {topic.lower()} and annotate "
        "where observability, security and cost controls belong.",
        f"Design an evaluation that would tell you whether {topic.lower()} is working in "
        "production, including the metric, the dataset and the acceptance threshold.",
        f"Identify two pitfalls relevant to {topic.lower()} in your environment and describe "
        "the early warning signals you would monitor.",
        f"Prototype the simplest implementation that demonstrates {topic.lower()}, then list "
        "exactly what would need to change to make it production-ready.",
    ]
    lead = _para(
        "Work through the following exercises. They are designed to move understanding from "
        "recognition to application - the level required for real engineering work - so "
        "prefer writing and building over merely reading."
    )
    body = "\n".join(f"{i+1}. {e}" for i, e in enumerate(exercises))
    return lead + "\n\n" + body


def compose_takeaways(domain: dict, topic: str, rng: random.Random) -> str:
    name = domain["name"]
    points = [
        f"{topic} is a systems concern in {name}: data, models and operations must be co-designed.",
        "Measurement is non-negotiable; define success metrics and evaluation before building.",
        "Favour the simplest design that meets the requirement, and add complexity only when evidence demands it.",
        "Security, cost and observability are first-class requirements, not afterthoughts.",
        "Document decisions so the system remains understandable and operable as it evolves.",
    ]
    lead = "Key takeaways from this chapter:"
    body = "\n".join(f"- {p}" for p in points)
    return lead + "\n\n" + body


def word_count(text: str) -> int:
    return len(text.split())
