"""
Financial knowledge base loader.

Loads concept entries from data/knowledge/financial_concepts.json
and provides simple keyword + topic search.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class Concept(TypedDict):
    id: str
    topic: str
    subtopic: str
    question_en: str
    answer_en: str
    tags: list[str]
    difficulty: str


_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "knowledge" / "financial_concepts.json"


def load_concepts() -> list[Concept]:
    """Load all financial concepts from the JSON knowledge base."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def search(query: str, top_k: int = 3) -> list[Concept]:
    """
    Simple keyword search over concepts.
    Searches question, answer, topic, and tags.
    Returns up to top_k results ordered by match score.
    """
    concepts = load_concepts()
    query_terms = query.lower().split()

    scored: list[tuple[int, Concept]] = []
    for concept in concepts:
        searchable = " ".join([
            concept["question_en"],
            concept["answer_en"],
            concept["topic"],
            concept["subtopic"],
            " ".join(concept["tags"]),
        ]).lower()

        score = sum(1 for term in query_terms if term in searchable)
        if score > 0:
            scored.append((score, concept))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [concept for _, concept in scored[:top_k]]
