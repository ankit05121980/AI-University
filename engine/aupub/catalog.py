"""Generate the catalog of 500+ books across the 33 AI categories.

Each category yields a series of books that approach the subject from a
different angle (foundations, hands-on, enterprise architecture, security,
operations, certification, etc.). Titles, metadata and identifiers are all
derived deterministically so the catalog is reproducible.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from .knowledge import CATEGORIES
from .models import slugify

# Each "angle" defines a distinct book within a category series.
# (suffix, level, audience descriptor)
SERIES_ANGLES: list[tuple[str, str, str]] = [
    ("Foundations", "Foundational", "newcomers building a rigorous base"),
    ("A Practitioner's Guide", "Intermediate", "engineers shipping real systems"),
    ("Enterprise Architecture Patterns", "Advanced", "architects designing at scale"),
    ("Hands-On Labs and Projects", "Intermediate", "learners who build to understand"),
    ("Advanced Techniques", "Advanced", "specialists pushing the frontier"),
    ("Security and Threat Modelling", "Advanced", "security engineers and risk owners"),
    ("Operations and Reliability", "Advanced", "platform and operations teams"),
    ("Governance, Risk and Compliance", "Intermediate", "governance and compliance leaders"),
    ("for Technical Leaders", "Intermediate", "engineering managers and leads"),
    ("for Executives and Strategy", "Foundational", "executives setting AI strategy"),
    ("Reference Architecture and Blueprints", "Advanced", "principal engineers and architects"),
    ("Performance and Cost Optimisation", "Advanced", "teams optimising at scale"),
    ("Testing, Evaluation and Quality", "Intermediate", "QA and ML quality engineers"),
    ("Certification Study Guide", "Intermediate", "candidates preparing for certification"),
    ("Case Studies and Field Notes", "Intermediate", "teams learning from real deployments"),
    ("The Complete Professional Reference", "Advanced", "experienced professionals"),
    ("Design Patterns and Anti-Patterns", "Advanced", "senior engineers and architects"),
    ("Production Playbook", "Advanced", "teams operating in production"),
]

AUTHOR_POOL = [
    "Dr. Amara Okafor", "Dr. Lukas Hoffmann", "Priya Narayanan", "Dr. Wei Chen",
    "Sofia Marchetti", "Dr. Daniel Rosenberg", "Aisha Rahman", "Dr. Marcus Webb",
    "Yuki Tanaka", "Dr. Elena Petrova", "Carlos Mendoza", "Dr. Ngozi Eze",
    "Hannah Lindqvist", "Dr. Rajesh Gupta", "Olivia Brandt", "Dr. Samuel Kim",
    "The AI-University Faculty",
]

LEVEL_PAGE_TARGET = {
    "Foundational": 250,
    "Intermediate": 270,
    "Advanced": 290,
}


@dataclass
class BookSpec:
    """Lightweight specification used to drive full generation."""

    id: str
    slug: str
    title: str
    subtitle: str
    category: str
    category_slug: str
    level: str
    target_pages: int
    audience: str
    seed: int
    series_index: int


def _isbn(seed: int) -> str:
    rng = random.Random(seed)
    digits = [9, 7, 8] + [rng.randint(0, 9) for _ in range(9)]
    # ISBN-13 check digit
    checksum = sum((1 if i % 2 == 0 else 3) * d for i, d in enumerate(digits))
    check = (10 - (checksum % 10)) % 10
    digits.append(check)
    s = "".join(str(d) for d in digits)
    return f"{s[0:3]}-{s[3]}-{s[4:9]}-{s[9:12]}-{s[12]}"


def build_specs(per_category: int = 16) -> list[BookSpec]:
    """Build deterministic specs for ``per_category`` books per category."""
    specs: list[BookSpec] = []
    counter = 0
    for cat in CATEGORIES:
        for i in range(per_category):
            angle, level, audience = SERIES_ANGLES[i % len(SERIES_ANGLES)]
            # Disambiguate if we wrap past the angle list.
            volume = "" if i < len(SERIES_ANGLES) else f", Volume {i // len(SERIES_ANGLES) + 1}"
            title = f"{cat['name']}: {angle}{volume}"
            slug = slugify(f"{cat['slug']}-{angle}{volume}")
            counter += 1
            book_id = f"AIU-{counter:04d}"
            seed = int(hashlib.sha256(book_id.encode()).hexdigest(), 16) % (2**31)
            target = LEVEL_PAGE_TARGET[level]
            subtitle = (
                f"{cat['tagline']} — a {level.lower()} guide for {audience}."
            )
            specs.append(
                BookSpec(
                    id=book_id,
                    slug=slug,
                    title=title,
                    subtitle=subtitle,
                    category=cat["name"],
                    category_slug=cat["slug"],
                    level=level,
                    target_pages=target,
                    audience=audience,
                    seed=seed,
                    series_index=i,
                )
            )
    return specs


def assign_authors(seed: int) -> list[str]:
    rng = random.Random(seed)
    n = rng.choice([1, 1, 2, 2, 3])
    authors = rng.sample(AUTHOR_POOL[:-1], n)
    if rng.random() < 0.3:
        authors.append("The AI-University Faculty")
    return authors
