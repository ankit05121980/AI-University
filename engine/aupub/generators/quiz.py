"""Assessment, certification and interview question generation.

Questions are derived from a domain's concepts, best practices and pitfalls so
they probe real understanding. Each multiple-choice item has one correct option,
three plausible distractors and an explanation.
"""
from __future__ import annotations

import random

from ..models import QuizQuestion

_GENERIC_DISTRACTORS = [
    "It eliminates the need for any evaluation or monitoring.",
    "It guarantees deterministic output regardless of input.",
    "It removes all security and governance requirements.",
    "It is only relevant to academic research, not production.",
    "It makes the system slower but has no other effect.",
    "It applies exclusively to image data.",
]


def _concept_question(domain: dict, concept: tuple[str, str],
                      rng: random.Random) -> QuizQuestion:
    title, desc = concept
    correct = f"{desc}"
    distractors = rng.sample(_GENERIC_DISTRACTORS, 3)
    options = [correct] + distractors
    rng.shuffle(options)
    answer_index = options.index(correct)
    return QuizQuestion(
        question=f"In the context of {domain['name']}, which statement best describes "
                 f"\u201c{title}\u201d?",
        options=options,
        answer_index=answer_index,
        explanation=f"{title}: {desc}",
        difficulty=rng.choice(["foundational", "intermediate", "advanced"]),
        kind="assessment",
    )


def _best_practice_question(domain: dict, rng: random.Random) -> QuizQuestion:
    practices = domain.get("best_practices", [])
    pitfalls = domain.get("pitfalls", [])
    if not practices:
        return _concept_question(domain, rng.choice(domain["concepts"]), rng)
    correct = rng.choice(practices)
    distractors_src = pitfalls + _GENERIC_DISTRACTORS
    distractors = rng.sample(distractors_src, min(3, len(distractors_src)))
    options = [correct] + distractors
    rng.shuffle(options)
    return QuizQuestion(
        question=f"Which of the following is a recommended best practice when working "
                 f"with {domain['name']}?",
        options=options,
        answer_index=options.index(correct),
        explanation=f"Best practice: {correct}",
        difficulty="intermediate",
        kind="certification",
    )


def _pitfall_question(domain: dict, rng: random.Random) -> QuizQuestion:
    pitfalls = domain.get("pitfalls", [])
    practices = domain.get("best_practices", [])
    if not pitfalls:
        return _best_practice_question(domain, rng)
    correct = rng.choice(pitfalls)
    distractors_src = practices + _GENERIC_DISTRACTORS
    distractors = rng.sample(distractors_src, min(3, len(distractors_src)))
    options = [correct] + distractors
    rng.shuffle(options)
    return QuizQuestion(
        question=f"Which of the following is a common pitfall to avoid in {domain['name']}?",
        options=options,
        answer_index=options.index(correct),
        explanation=f"Pitfall to avoid: {correct}",
        difficulty="intermediate",
        kind="certification",
    )


INTERVIEW_TEMPLATES = [
    "Explain {topic} and why it matters in a production {name} system.",
    "Walk through how you would design {topic} for an enterprise {name} workload.",
    "What trade-offs would you weigh when implementing {topic}?",
    "How would you test and monitor {topic} in production?",
    "Describe a failure mode of {topic} and how you would mitigate it.",
    "How does {topic} interact with security and governance requirements?",
]


def make_interview_question(domain: dict, concept: tuple[str, str],
                            rng: random.Random) -> QuizQuestion:
    title, desc = concept
    template = rng.choice(INTERVIEW_TEMPLATES)
    q = template.format(topic=title, name=domain["name"])
    model_answer = (
        f"A strong answer defines {title.lower()} ({desc}) then connects it to "
        f"architecture, evaluation, cost, security and operations for {domain['name']}, "
        f"citing concrete trade-offs and a real-world example."
    )
    return QuizQuestion(
        question=q,
        options=[],
        answer_index=-1,
        explanation=model_answer,
        difficulty="advanced",
        kind="interview",
    )


def make_questions(domain: dict, concept: tuple[str, str], rng: random.Random,
                   n_mc: int = 3, n_interview: int = 1) -> list[QuizQuestion]:
    """Produce a mix of MC (assessment + certification) and interview questions."""
    out: list[QuizQuestion] = []
    builders = [
        lambda: _concept_question(domain, concept, rng),
        lambda: _best_practice_question(domain, rng),
        lambda: _pitfall_question(domain, rng),
    ]
    for i in range(n_mc):
        out.append(builders[i % len(builders)]())
    for _ in range(n_interview):
        out.append(make_interview_question(domain, concept, rng))
    return out
