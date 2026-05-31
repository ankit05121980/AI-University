"""Code-sample generation.

Produces illustrative, syntactically valid code listings in the domain's
primary language, themed to the chapter topic. The samples are deliberately
realistic (typed, documented, error-handled) to match enterprise standards.
"""
from __future__ import annotations

import random

from ..models import CodeSample


def _py_dataclass(topic: str, domain: dict) -> CodeSample:
    cls = "".join(w.capitalize() for w in topic.split()[:3] if w.isalpha()) or "Component"
    code = f'''from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class {cls}Config:
    """Configuration for the {topic} component in a {domain['name']} system."""

    name: str
    timeout_s: float = 30.0
    max_retries: int = 3
    options: dict[str, Any] = field(default_factory=dict)


class {cls}:
    """A minimal, production-shaped implementation of {topic}."""

    def __init__(self, config: {cls}Config) -> None:
        self._config = config
        self._calls = 0

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process a request, retrying transient failures with backoff."""
        last_error: Exception | None = None
        for attempt in range(self._config.max_retries):
            try:
                self._calls += 1
                return self._process(payload)
            except TimeoutError as exc:  # transient
                last_error = exc
                continue
        raise RuntimeError(f"{cls} failed after retries") from last_error

    def _process(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Domain-specific logic for {topic} goes here.
        return {{"status": "ok", "input_keys": sorted(payload), "calls": self._calls}}
'''
    return CodeSample(
        title=f"Implementing a {topic} component",
        language="python",
        code=code,
        explanation=(
            f"This listing shows a configuration-driven {topic} component with retry "
            f"semantics and typed interfaces — the shape we expect from production "
            f"{domain['name']} code rather than a notebook prototype."
        ),
    )


def _py_pipeline(topic: str, domain: dict) -> CodeSample:
    code = f'''from collections.abc import Iterable, Iterator
from typing import Protocol


class Stage(Protocol):
    def __call__(self, item: dict) -> dict: ...


def pipeline(stages: list[Stage]) -> Stage:
    """Compose ordered stages into a single callable for {topic}."""

    def run(item: dict) -> dict:
        for stage in stages:
            item = stage(item)
        return item

    return run


def validate(item: dict) -> dict:
    if "text" not in item:
        raise ValueError("missing required field: text")
    return item


def normalise(item: dict) -> dict:
    item["text"] = item["text"].strip().lower()
    return item


def enrich(item: dict) -> dict:
    item["length"] = len(item["text"])
    return item


process = pipeline([validate, normalise, enrich])


def run_batch(items: Iterable[dict]) -> Iterator[dict]:
    for item in items:
        try:
            yield process(dict(item))
        except ValueError as exc:
            yield {{"error": str(exc), "item": item}}
'''
    return CodeSample(
        title=f"A composable processing pipeline for {topic}",
        language="python",
        code=code,
        explanation=(
            f"Pipelines keep {topic} logic modular and testable. Each stage is a pure "
            "function, errors are captured per item, and the composition is trivial to "
            "extend or reorder."
        ),
    )


def _py_eval(topic: str, domain: dict) -> CodeSample:
    code = f'''from dataclasses import dataclass


@dataclass
class EvalResult:
    metric: str
    score: float
    passed: bool


def evaluate(predictions: list[str], references: list[str],
             threshold: float = 0.8) -> EvalResult:
    """Score {topic} output against references with a simple exact-match metric.

    In practice you would combine several metrics (exact match, semantic
    similarity, LLM-as-judge) and gate releases on the aggregate.
    """
    if len(predictions) != len(references):
        raise ValueError("predictions and references must align")
    hits = sum(p.strip() == r.strip() for p, r in zip(predictions, references))
    score = hits / len(references) if references else 0.0
    return EvalResult(metric="exact_match", score=score, passed=score >= threshold)


if __name__ == "__main__":
    result = evaluate(["yes", "no"], ["yes", "yes"])
    print(f"{{result.metric}}={{result.score:.2f}} passed={{result.passed}}")
'''
    return CodeSample(
        title=f"Evaluating {topic} with a regression gate",
        language="python",
        code=code,
        explanation=(
            f"Every change to a {domain['name']} system should pass an evaluation gate. "
            "This example shows the minimal shape: align predictions and references, "
            "compute a metric, and return a pass/fail decision for CI."
        ),
    )


def _ts_module(topic: str, domain: dict) -> CodeSample:
    cls = "".join(w.capitalize() for w in topic.split()[:3] if w.isalpha()) or "Component"
    code = f'''export interface {cls}Config {{
  name: string;
  timeoutMs?: number;
  maxRetries?: number;
}}

export interface Result<T> {{
  ok: boolean;
  value?: T;
  error?: string;
}}

/** A production-shaped {topic} component for a {domain['name']} system. */
export class {cls} {{
  private calls = 0;

  constructor(private readonly config: {cls}Config) {{}}

  async run(payload: Record<string, unknown>): Promise<Result<Record<string, unknown>>> {{
    const retries = this.config.maxRetries ?? 3;
    for (let attempt = 0; attempt < retries; attempt++) {{
      try {{
        this.calls++;
        return {{ ok: true, value: await this.process(payload) }};
      }} catch (err) {{
        if (attempt === retries - 1) {{
          return {{ ok: false, error: (err as Error).message }};
        }}
      }}
    }}
    return {{ ok: false, error: "unreachable" }};
  }}

  private async process(payload: Record<string, unknown>): Promise<Record<string, unknown>> {{
    return {{ status: "ok", keys: Object.keys(payload), calls: this.calls }};
  }}
}}
'''
    return CodeSample(
        title=f"A typed {topic} module",
        language="typescript",
        code=code,
        explanation=(
            f"Strong typing and explicit Result types make {topic} integrations safe to "
            f"consume across a {domain['name']} codebase."
        ),
    )


_PY_TEMPLATES = [_py_dataclass, _py_pipeline, _py_eval]
_TS_TEMPLATES = [_ts_module, _py_pipeline]  # ts module + a generic example


def make_code_sample(domain: dict, topic: str, rng: random.Random) -> CodeSample:
    language = domain.get("language", "python")
    if language == "typescript":
        fn = rng.choice([_ts_module])
    else:
        fn = rng.choice(_PY_TEMPLATES)
    return fn(topic, domain)
