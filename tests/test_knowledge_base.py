"""Tests for the financial knowledge base."""
import pytest
from finling.knowledge.base import load_concepts, search


def test_load_concepts_returns_list():
    concepts = load_concepts()
    assert isinstance(concepts, list)
    assert len(concepts) > 0


def test_each_concept_has_required_keys():
    required = {"id", "topic", "question_en", "answer_en", "tags"}
    for concept in load_concepts():
        assert required.issubset(concept.keys())


def test_search_returns_results_for_known_topic():
    results = search("savings")
    assert len(results) > 0
    assert any("savings" in r["topic"] for r in results)


def test_search_returns_empty_for_unknown_topic():
    results = search("xyzzy_unknown_term_12345")
    assert results == []


def test_search_top_k_limit():
    results = search("money bank loan savings", top_k=2)
    assert len(results) <= 2
