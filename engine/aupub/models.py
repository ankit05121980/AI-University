"""Core data models for the publishing platform.

These dataclasses describe the structure of a book, its chapters and the
artefacts produced for it. They are intentionally serialisable to JSON so
that the web portal can consume them directly without a database.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from typing import Any


def slugify(value: str) -> str:
    """Convert an arbitrary title into a URL/file-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


@dataclass
class Diagram:
    """A professional diagram rendered in one of several source formats."""

    title: str
    kind: str  # architecture, sequence, dataflow, deployment, ...
    fmt: str  # mermaid | plantuml | svg | drawio
    source: str
    caption: str = ""
    render_svg: str = ""  # always-available, self-contained SVG for viewers

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class CodeSample:
    """An executable / illustrative code listing."""

    title: str
    language: str
    code: str
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class QuizQuestion:
    """A single assessment / certification style question."""

    question: str
    options: list[str]
    answer_index: int
    explanation: str
    difficulty: str = "intermediate"
    kind: str = "assessment"  # assessment | certification | interview

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Section:
    """A named block of prose / content inside a chapter."""

    heading: str
    body: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Chapter:
    number: int
    title: str
    summary: str = ""
    sections: list[Section] = field(default_factory=list)
    diagrams: list[Diagram] = field(default_factory=list)
    code_samples: list[CodeSample] = field(default_factory=list)
    questions: list[QuizQuestion] = field(default_factory=list)
    estimated_pages: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections],
            "diagrams": [d.to_dict() for d in self.diagrams],
            "code_samples": [c.to_dict() for c in self.code_samples],
            "questions": [q.to_dict() for q in self.questions],
            "estimated_pages": self.estimated_pages,
        }


@dataclass
class FrontMatter:
    """The structured front/back matter required for every document."""

    executive_summary: str = ""
    learning_objectives: list[str] = field(default_factory=list)
    industry_context: str = ""
    business_perspective: str = ""
    technical_perspective: str = ""
    architecture_perspective: str = ""
    governance_perspective: str = ""
    security_perspective: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class BackMatter:
    references: list[str] = field(default_factory=list)
    glossary: list[dict[str, str]] = field(default_factory=list)
    index_terms: list[str] = field(default_factory=list)
    case_studies: list[dict[str, str]] = field(default_factory=list)
    labs: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Book:
    id: str
    slug: str
    title: str
    subtitle: str
    category: str
    category_slug: str
    level: str
    edition: str
    version: str
    authors: list[str]
    keywords: list[str]
    description: str
    isbn: str
    published: str
    estimated_pages: int = 0
    word_count: int = 0
    diagram_count: int = 0
    code_count: int = 0
    question_count: int = 0
    chapter_count: int = 0
    front_matter: FrontMatter = field(default_factory=FrontMatter)
    back_matter: BackMatter = field(default_factory=BackMatter)
    chapters: list[Chapter] = field(default_factory=list)

    def to_dict(self, *, include_content: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "subtitle": self.subtitle,
            "category": self.category,
            "category_slug": self.category_slug,
            "level": self.level,
            "edition": self.edition,
            "version": self.version,
            "authors": self.authors,
            "keywords": self.keywords,
            "description": self.description,
            "isbn": self.isbn,
            "published": self.published,
            "estimated_pages": self.estimated_pages,
            "word_count": self.word_count,
            "diagram_count": self.diagram_count,
            "code_count": self.code_count,
            "question_count": self.question_count,
            "chapter_count": self.chapter_count,
        }
        if include_content:
            data["front_matter"] = self.front_matter.to_dict()
            data["back_matter"] = self.back_matter.to_dict()
            data["chapters"] = [c.to_dict() for c in self.chapters]
        return data

    def catalog_entry(self) -> dict[str, Any]:
        """A lightweight record used by the portal's library/index."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "subtitle": self.subtitle,
            "category": self.category,
            "category_slug": self.category_slug,
            "level": self.level,
            "edition": self.edition,
            "version": self.version,
            "authors": self.authors,
            "keywords": self.keywords,
            "description": self.description,
            "isbn": self.isbn,
            "published": self.published,
            "estimated_pages": self.estimated_pages,
            "word_count": self.word_count,
            "diagram_count": self.diagram_count,
            "code_count": self.code_count,
            "question_count": self.question_count,
            "chapter_count": self.chapter_count,
        }
