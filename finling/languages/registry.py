"""
Language registry for FinLing.

Each language entry defines:
- code:        BCP-47 / ISO 639-3 code
- name:        English name
- native_name: Name in the language itself
- region:      Primary region
- ghana_nlp_model: GhanaNLP HuggingFace model identifier for translation (en <-> lang)
- supported:   Whether this language is fully active in the pipeline
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Language:
    code: str
    name: str
    native_name: str
    region: str
    ghana_nlp_translation_model: str | None
    supported: bool = False


# ---------------------------------------------------------------------------
# Registered languages
# ---------------------------------------------------------------------------
LANGUAGES: dict[str, Language] = {
    "tw": Language(
        code="tw",
        name="Twi (Akan)",
        native_name="Twi",
        region="Ashanti, Eastern, Central Ghana",
        ghana_nlp_translation_model="Helsinki-NLP/opus-mt-tw-en",
        supported=True,
    ),
    "ga": Language(
        code="ga",
        name="Ga",
        native_name="Gã",
        region="Greater Accra, Ghana",
        ghana_nlp_translation_model=None,  # to be added
        supported=False,
    ),
    "ee": Language(
        code="ee",
        name="Ewe",
        native_name="Eʋegbe",
        region="Volta Region, Ghana",
        ghana_nlp_translation_model="Helsinki-NLP/opus-mt-ee-en",
        supported=False,
    ),
    "dag": Language(
        code="dag",
        name="Dagbani",
        native_name="Dagbanli",
        region="Northern Region, Ghana",
        ghana_nlp_translation_model=None,  # to be added
        supported=False,
    ),
    # --- Future: NigerianNLP contributions welcome below ---
    "yo": Language(
        code="yo",
        name="Yoruba",
        native_name="Yorùbá",
        region="Nigeria",
        ghana_nlp_translation_model="Helsinki-NLP/opus-mt-yo-en",
        supported=False,
    ),
    "ig": Language(
        code="ig",
        name="Igbo",
        native_name="Igbo",
        region="Nigeria",
        ghana_nlp_translation_model=None,
        supported=False,
    ),
}


def get_language(code: str) -> Language:
    """Return a Language by its code. Raises KeyError if not found."""
    try:
        return LANGUAGES[code]
    except KeyError:
        supported = [k for k, v in LANGUAGES.items() if v.supported]
        raise KeyError(
            f"Language '{code}' not found. Supported codes: {supported}"
        ) from None


def supported_languages() -> list[Language]:
    """Return only languages that are currently active in the pipeline."""
    return [lang for lang in LANGUAGES.values() if lang.supported]
