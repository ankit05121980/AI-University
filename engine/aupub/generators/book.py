"""Assemble a complete :class:`Book` from a :class:`BookSpec`.

This is the orchestration layer of the content engine. It expands a spec into
front matter, 20-30 chapters (each with theory, architecture, deep dives,
examples, code, exercises, use cases, best practices, pitfalls, governance
notes and review questions), professional diagrams, and full back matter
(references, glossary, index, case studies and hands-on labs). All metrics
(words, pages, diagrams, code, questions) are computed from the actual
generated content.
"""
from __future__ import annotations

import random

from ..catalog import BookSpec, assign_authors
from ..knowledge import get_domain
from ..models import (
    BackMatter, Book, Chapter, CodeSample, Diagram, FrontMatter, QuizQuestion, Section,
)
from . import code as codegen
from . import diagrams as diaggen
from . import prose
from . import quiz as quizgen

WORDS_PER_PAGE = 300
FIXED_FRONTBACK_PAGES = 14  # cover, copyright, toc, lof, lot, glossary, index, refs
DIAGRAM_PAGE_WEIGHT = 0.6
CODE_PAGE_WEIGHT = 0.7
QUESTION_PAGE_WEIGHT = 0.14


def _extra_chapter_topics(domain: dict) -> list[tuple[str, str]]:
    name = domain["name"]
    uc = domain.get("use_cases", [(name, "a representative workload")])
    industry = uc[0][0] if uc else "Enterprise"
    return [
        ("Putting It Together: A Reference Implementation",
         f"an end-to-end reference implementation that integrates the components of a {name} system into a cohesive, working whole"),
        (f"Hands-On Lab: Building an End-to-End {name} System",
         f"a guided, build-along laboratory that constructs a functioning {name} system from first principles"),
        (f"Case Study: {industry} at Scale",
         f"a detailed case study of deploying {name} in a demanding {industry.lower()} environment, including the decisions, trade-offs and outcomes"),
        ("Operating in Production",
         f"the operational discipline required to run a {name} system reliably, including monitoring, incident response and continuous improvement"),
        ("Evaluation and Quality Assurance",
         f"a rigorous approach to measuring and assuring the quality of a {name} system before and after release"),
        ("Security, Privacy and Governance",
         f"the security, privacy and governance controls that make a {name} system trustworthy and compliant"),
        ("Cost, Performance and Scaling",
         f"techniques for controlling cost and latency while scaling a {name} system to production traffic"),
        ("Integration and Interoperability",
         f"patterns for integrating a {name} system with surrounding enterprise systems and data"),
        ("Trends and Research Directions",
         f"emerging trends, open problems and research directions shaping the future of {name}"),
        ("Capstone Project",
         f"a substantial capstone project that consolidates the entire book into a portfolio-grade {name} deliverable"),
        ("Certification Preparation and Review",
         f"a structured review and certification-style preparation covering the full breadth of {name}"),
    ]


def _build_sections(domain: dict, topic: str, desc: str, rng: random.Random,
                    related: list[tuple[str, str]]) -> list[Section]:
    related2 = list(related)
    rng.shuffle(related2)
    return [
        Section("Introduction", prose.compose_intro(domain, topic, desc, rng)),
        Section("Theory and Foundations",
                prose.compose_theory(domain, topic, desc, rng, related)),
        Section("Architecture and Design",
                prose.compose_architecture(domain, topic, rng)),
        Section("Deep Dive: Mechanics, Variants and Trade-offs",
                prose.compose_deep_dive(domain, topic, rng, related)),
        Section("Advanced Considerations",
                prose.compose_deep_dive(domain, topic, rng, related2)),
        Section("Worked Example", prose.compose_example(domain, topic, rng)),
        Section("Industry Use Cases", prose.compose_use_cases(domain, rng)),
        Section("Best Practices", prose.compose_best_practices(domain, topic, rng)),
        Section("Common Pitfalls", prose.compose_pitfalls(domain, topic, rng)),
        Section("Governance, Security and Cost Notes",
                prose.compose_governance_notes(domain, topic, rng)),
        Section("Hands-On Exercises", prose.compose_exercises(domain, topic, rng)),
        Section("Key Takeaways", prose.compose_takeaways(domain, topic, rng)),
    ]


def _chapter_summary(domain: dict, topic: str, desc: str) -> str:
    return (
        f"This chapter examines {topic.lower()} within {domain['name']}. "
        f"It covers {prose._desc_low(desc)}, derives a reference architecture, walks "
        f"through a worked example and runnable code, surveys industry use cases, and "
        f"distils best practices and pitfalls, closing with exercises and review questions."
    )


def build_book(spec: BookSpec) -> Book:
    domain = get_domain(spec.category_slug)
    rng = random.Random(spec.seed)

    concepts: list[tuple[str, str]] = list(domain["concepts"])
    extra = _extra_chapter_topics(domain)
    topics = concepts + extra
    topics = topics[:30]
    if len(topics) < 20:
        topics = (topics * 2)[:20]

    diagram_kinds = list(diaggen.DIAGRAM_KINDS)
    rng.shuffle(diagram_kinds)

    chapters: list[Chapter] = []
    total_words = 0
    total_diagrams = 0
    total_code = 0
    total_questions = 0
    all_index_terms: set[str] = set()

    for idx, (topic, desc) in enumerate(topics):
        related = [c for c in concepts if c[0] != topic]
        rng.shuffle(related)
        sections = _build_sections(domain, topic, desc, rng, related)
        chap_words = sum(prose.word_count(s.body) for s in sections)

        n_diag = 1 + (1 if rng.random() < 0.35 else 0)
        # Per-chapter diagram context: centre the figures on this chapter's topic
        # so diagrams differ from chapter to chapter instead of repeating.
        chap_dom = {**domain, "name": topic, "concepts": [(topic, desc)] + related,
                    "_ordered": True}
        cdiagrams: list[Diagram] = []
        for d in range(n_diag):
            kind = diagram_kinds[(idx + d) % len(diagram_kinds)]
            dtitle = f"{kind} - {topic}"
            cdiagrams.append(diaggen.make_diagram(chap_dom, kind, dtitle, rng))

        ccode: list[CodeSample] = []
        if topic not in ("Trends and Research Directions",):
            ccode.append(codegen.make_code_sample(domain, topic, rng))
            sections.append(Section(
                "Code Walkthrough",
                ccode[-1].explanation + "\n\nThe full listing is shown below; study it "
                "line by line and reproduce it locally before moving on.",
            ))
            chap_words += prose.word_count(sections[-1].body)

        cquestions: list[QuizQuestion] = quizgen.make_questions(domain, (topic, desc), rng)

        pages = (
            chap_words / WORDS_PER_PAGE
            + len(cdiagrams) * DIAGRAM_PAGE_WEIGHT
            + len(ccode) * CODE_PAGE_WEIGHT
            + len(cquestions) * QUESTION_PAGE_WEIGHT
        )

        chapters.append(Chapter(
            number=idx + 1,
            title=topic,
            summary=_chapter_summary(domain, topic, desc),
            sections=sections,
            diagrams=cdiagrams,
            code_samples=ccode,
            questions=cquestions,
            estimated_pages=max(8, round(pages)),
        ))
        total_words += chap_words
        total_diagrams += len(cdiagrams)
        total_code += len(ccode)
        total_questions += len(cquestions)
        all_index_terms.add(topic)
        for g, _ in domain.get("glossary", []):
            all_index_terms.add(g)

    fm = _build_front_matter(domain, spec, rng)
    total_words += _front_matter_words(fm)

    bm = _build_back_matter(domain, spec, rng, sorted(all_index_terms))
    total_words += sum(prose.word_count(cs["body"]) for cs in bm.case_studies)
    total_words += sum(prose.word_count(lab["body"]) for lab in bm.labs)

    estimated_pages = round(
        total_words / WORDS_PER_PAGE
        + total_diagrams * DIAGRAM_PAGE_WEIGHT
        + total_code * CODE_PAGE_WEIGHT
        + total_questions * QUESTION_PAGE_WEIGHT
        + FIXED_FRONTBACK_PAGES
    )

    authors = assign_authors(spec.seed)

    return Book(
        id=spec.id,
        slug=spec.slug,
        title=spec.title,
        subtitle=spec.subtitle,
        category=spec.category,
        category_slug=spec.category_slug,
        level=spec.level,
        edition="First Edition",
        version="1.0.0",
        authors=authors,
        keywords=_keywords(domain, spec),
        description=spec.subtitle,
        isbn=_isbn(spec),
        published="2026",
        estimated_pages=estimated_pages,
        word_count=total_words,
        diagram_count=total_diagrams,
        code_count=total_code,
        question_count=total_questions,
        chapter_count=len(chapters),
        front_matter=fm,
        back_matter=bm,
        chapters=chapters,
    )


def _isbn(spec: BookSpec) -> str:
    from ..catalog import _isbn as isbn_fn

    return isbn_fn(spec.seed)


def _keywords(domain: dict, spec: BookSpec) -> list[str]:
    kws = [domain["name"], spec.level, "Enterprise AI", "Professional"]
    kws += [c[0] for c in domain["concepts"][:4]]
    return kws


def _front_matter_words(fm: FrontMatter) -> int:
    n = 0
    for v in (fm.executive_summary, fm.industry_context, fm.business_perspective,
              fm.technical_perspective, fm.architecture_perspective,
              fm.governance_perspective, fm.security_perspective):
        n += prose.word_count(v)
    n += sum(prose.word_count(o) for o in fm.learning_objectives)
    return n


def _build_front_matter(domain: dict, spec: BookSpec, rng: random.Random) -> FrontMatter:
    name = domain["name"]
    overview = domain["overview"]
    objectives = [
        f"Explain the foundational principles of {name} and articulate where it creates value.",
        f"Design a reference architecture for a {name} system that meets enterprise quality attributes.",
        f"Implement core {name} components following production engineering standards.",
        f"Evaluate {name} systems rigorously and gate releases on measurable quality.",
        f"Apply security, privacy and governance controls appropriate to {name}.",
        f"Operate {name} systems reliably, controlling cost, latency and drift.",
        f"Recognise common pitfalls in {name} and apply proven mitigations.",
    ]
    exec_summary = prose._para(
        overview,
        f"This volume is written for {spec.audience}. It progresses from first principles "
        f"to enterprise-grade design and operations, with every chapter combining theory, "
        f"architecture, worked examples, runnable code, exercises and assessment.",
        "The treatment is deliberately practical: the emphasis throughout is on decisions "
        "that hold up in production, backed by measurement rather than intuition.",
    )
    industry = prose._para(
        f"{name} sits within a rapidly maturing AI landscape in which organisations are "
        "moving from experimentation to dependable, governed deployment.",
        "The competitive advantage no longer comes from access to models alone but from the "
        "engineering and operational discipline that turns capability into reliable, "
        "compliant business outcomes.",
        "This book situates the subject in that context so readers can connect technical "
        "choices to organisational value.",
    )
    business = prose._para(
        f"From a business perspective, {name} initiatives must be justified by clear value: "
        "revenue growth, cost reduction, risk mitigation or improved experience.",
        "Leaders should insist on measurable objectives, realistic unit economics that "
        "account for inference cost, and a roadmap that sequences capability against risk.",
        "The most common failure is not technical but strategic: building capability that is "
        "never connected to a decision or workflow that matters.",
    )
    technical = prose._para(
        f"The technical perspective treats {name} as a systems discipline.",
        domain.get("architecture", ""),
        "Throughout, the book favours clear interfaces, reproducibility and measurement.",
    )
    architecture = prose._para(
        f"Architecturally, a {name} platform is layered into data, model, application and "
        "operations planes, each with explicit contracts so they can evolve independently.",
        "A model gateway centralises access and control; observability and security are "
        "cross-cutting and designed in from the start.",
        "Reference architectures and blueprints appear in every chapter and are consolidated "
        "in the capstone.",
    )
    governance = prose._para(
        f"Governance ensures {name} is developed and used responsibly, legally and in line "
        "with organisational values.",
        "This book embeds governance as lifecycle gates - risk classification, documentation, "
        "approval and monitoring - rather than as a final checkpoint, aligning with frameworks "
        "such as the NIST AI RMF, ISO/IEC 42001 and the EU AI Act.",
    )
    security = prose._para(
        f"Security for {name} extends traditional controls with ML-specific defences against "
        "prompt injection, data poisoning, model extraction and insecure output handling.",
        "Defence in depth - input validation, constrained decoding, output validation, "
        "sandboxed tools and continuous monitoring - is applied consistently, mapped to the "
        "OWASP LLM Top 10 and MITRE ATLAS.",
    )
    return FrontMatter(
        executive_summary=exec_summary,
        learning_objectives=objectives,
        industry_context=industry,
        business_perspective=business,
        technical_perspective=technical,
        architecture_perspective=architecture,
        governance_perspective=governance,
        security_perspective=security,
    )


def _build_back_matter(domain: dict, spec: BookSpec, rng: random.Random,
                       index_terms: list[str]) -> BackMatter:
    name = domain["name"]
    refs = list(domain.get("references", []))
    refs += [
        "NIST - Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
        "ISO/IEC 42001:2023 - Information technology - AI management system",
        "OWASP - Top 10 for Large Language Model Applications",
        "AI-University - Enterprise AI Reference Architecture (this series)",
    ]
    glossary = [{"term": t, "definition": d} for t, d in domain.get("glossary", [])]
    glossary += [
        {"term": "Foundation model", "definition": "A large model pre-trained on broad data and adaptable to many tasks."},
        {"term": "Evaluation gate", "definition": "An automated quality check that must pass before release."},
        {"term": "Observability", "definition": "The ability to understand a system's internal state from its outputs."},
    ]

    use_cases = domain.get("use_cases", [(name, "a representative workload")])
    case_studies = []
    for industry, scenario in use_cases[:3]:
        body = prose._para(
            f"**Context.** A {industry.lower()} organisation set out to apply {name} to "
            f"{prose._desc_low(scenario)}.",
            "**Approach.** The team began with a precise objective and an evaluation set, "
            "prototyped the simplest viable design, then hardened it with monitoring, "
            "security controls and cost budgets.",
            "**Outcome.** Measured against the original metric, the system delivered durable "
            "value because the surrounding engineering - data quality, evaluation and "
            "operations - was treated as seriously as the model itself.",
            "**Lessons.** Start with measurement, resist premature complexity, and design "
            "governance and observability in from day one.",
        )
        case_studies.append({"title": f"{industry}: {name} in Practice", "body": body})

    labs = []
    for i in range(2):
        body = prose._para(
            f"**Objective.** Build a working slice of a {name} system that demonstrates the "
            "core concepts end to end.",
            "**Steps.** (1) Define the objective and success metric. (2) Assemble a minimal "
            "dataset or fixtures. (3) Implement the core component using the patterns from "
            "the chapters. (4) Add an evaluation gate. (5) Instrument observability. (6) "
            "Document the design decisions in an architecture decision record.",
            "**Deliverable.** A reproducible repository with code, an evaluation report and a "
            "short design document suitable for a portfolio.",
        )
        labs.append({"title": f"Lab {i+1}: End-to-End {name} Build", "body": body})

    return BackMatter(
        references=refs,
        glossary=glossary,
        index_terms=index_terms,
        case_studies=case_studies,
        labs=labs,
    )
