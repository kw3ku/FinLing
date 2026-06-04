"""Tests for the language registry."""
import pytest
from finling.languages.registry import get_language, supported_languages, LANGUAGES


def test_all_languages_have_required_fields():
    for code, lang in LANGUAGES.items():
        assert lang.code == code
        assert lang.name
        assert lang.native_name


def test_get_language_returns_correct_entry():
    twi = get_language("tw")
    assert twi.name == "Twi (Akan)"
    assert twi.supported is True


def test_get_language_raises_for_unknown_code():
    with pytest.raises(KeyError):
        get_language("xx_unknown")


def test_supported_languages_returns_only_active():
    langs = supported_languages()
    assert all(lang.supported for lang in langs)
    assert any(lang.code == "tw" for lang in langs)
