"""
Core NLP pipeline for FinLing.

Flow:
    user_input (local language)
        → detect language
        → translate to English  (GhanaNLP model)
        → search knowledge base
        → format response
        → translate back to user language
        → return response
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from langdetect import detect, LangDetectException

from finling.knowledge.base import search, Concept
from finling.languages.registry import get_language, supported_languages, Language

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    original_query: str
    detected_language: str
    english_query: str
    concepts: list[Concept]
    response_en: str
    response_local: str


class FinLingPipeline:
    """
    Main query pipeline.

    On first use, translation models are lazy-loaded so startup is fast.
    """

    def __init__(self) -> None:
        self._translators: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(self, text: str, lang_code: str | None = None) -> QueryResult:
        """
        Process a financial query in any supported language.

        Args:
            text:      The user's question (in their local language or English).
            lang_code: Optional BCP-47 code (e.g. "tw"). If None, auto-detects.

        Returns:
            QueryResult with English and local-language response.
        """
        detected = lang_code or self._detect_language(text)
        english_query = self._to_english(text, detected)
        concepts = search(english_query)
        response_en = self._build_response(english_query, concepts)
        response_local = self._from_english(response_en, detected)

        return QueryResult(
            original_query=text,
            detected_language=detected,
            english_query=english_query,
            concepts=concepts,
            response_en=response_en,
            response_local=response_local,
        )

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def _detect_language(self, text: str) -> str:
        """
        Detect language using langdetect.
        Falls back to "en" if detection fails or returns an unsupported code.
        """
        try:
            code = detect(text)
            # langdetect may return "en" for Twi text — check supported langs
            supported_codes = {lang.code for lang in supported_languages()}
            return code if code in supported_codes else "en"
        except LangDetectException:
            logger.warning("Language detection failed, defaulting to English.")
            return "en"

    # ------------------------------------------------------------------
    # Translation helpers (lazy-load GhanaNLP / Helsinki models)
    # ------------------------------------------------------------------

    def _to_english(self, text: str, lang_code: str) -> str:
        """Translate text to English. Returns original text if lang is 'en'."""
        if lang_code == "en":
            return text
        translator = self._get_translator(lang_code, direction="to_en")
        if translator is None:
            logger.warning("No translation model for '%s'. Using original text.", lang_code)
            return text
        return self._run_translation(translator, text)

    def _from_english(self, text: str, lang_code: str) -> str:
        """Translate English response back to the target language."""
        if lang_code == "en":
            return text
        translator = self._get_translator(lang_code, direction="from_en")
        if translator is None:
            return text
        return self._run_translation(translator, text)

    def _get_translator(self, lang_code: str, direction: str) -> object | None:
        """
        Lazy-load a HuggingFace translation pipeline for the given language.
        Returns None if no model is configured.
        """
        cache_key = f"{lang_code}_{direction}"
        if cache_key in self._translators:
            return self._translators[cache_key]

        try:
            lang = get_language(lang_code)
        except KeyError:
            return None

        if lang.ghana_nlp_translation_model is None:
            return None

        try:
            from transformers import pipeline  # type: ignore

            model_id = lang.ghana_nlp_translation_model
            # For direction "from_en" we need the inverse model
            # GhanaNLP models follow the pattern opus-mt-{src}-{tgt}
            if direction == "from_en":
                parts = model_id.split("-")
                # swap src/tgt: opus-mt-tw-en → opus-mt-en-tw
                if len(parts) >= 2:
                    model_id = "-".join(parts[:-2] + [parts[-1], parts[-2]])

            logger.info("Loading translation model: %s", model_id)
            translator = pipeline("translation", model=model_id)
            self._translators[cache_key] = translator
            return translator

        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load model '%s': %s", model_id, exc)
            return None

    @staticmethod
    def _run_translation(translator: object, text: str) -> str:
        """Run a HuggingFace translation pipeline and return the translated string."""
        result = translator(text, max_length=512)  # type: ignore[operator]
        if result and isinstance(result, list):
            return result[0].get("translation_text", text)
        return text

    # ------------------------------------------------------------------
    # Response builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_response(query: str, concepts: list[Concept]) -> str:
        """
        Build a plain-English response from retrieved concepts.
        Phase 1: template-based. Phase 2: LLM-augmented.
        """
        if not concepts:
            return (
                "I'm sorry, I don't have information on that topic yet. "
                "Try asking about savings, loans, mobile money, budgeting, or insurance."
            )

        top = concepts[0]
        response = top["answer_en"]

        if len(concepts) > 1:
            related = ", ".join(c["topic"] for c in concepts[1:])
            response += f"\n\nRelated topics: {related}."

        return response
