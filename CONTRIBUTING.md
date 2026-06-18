# Contributing to FinLing

Thank you for helping make financial education accessible in African languages. **You do not need to be a programmer to contribute.** A Twi, Ga, Ewe, Dagbani, Yoruba, or Igbo speaker who can validate a sentence is just as valuable as a Python developer.

This guide explains the different ways to contribute and how to get your work merged.

---

## Ways to Contribute

| I want to... | Skill needed | Where |
|---|---|---|
| Add or correct financial content | None — just a text editor | [`data/knowledge/financial_concepts.json`](data/knowledge/financial_concepts.json) |
| Validate or add sentence translations | Native/fluent speaker | [`data/corpora/`](data/corpora/) |
| Add a new language | A bit of editing | [`finling/languages/registry.py`](finling/languages/registry.py) |
| Improve glossary terms | Native/fluent speaker | [`data/glossary/`](data/glossary/) |
| Fix bugs / build features | Python | [`finling/`](finling/) |
| Improve docs | Writing | `README.md`, this file |

> **New here?** Look for issues labelled **`good first issue`** on GitHub. They are scoped to be completable in one sitting.

---

## 1. Contribute Financial Content (no coding)

The knowledge base is a plain JSON file. To add a financial concept, add an object to [`data/knowledge/financial_concepts.json`](data/knowledge/financial_concepts.json):

```json
{
  "id": "savings-003",
  "topic": "savings",
  "subtopic": "emergency_fund",
  "question_en": "What is an emergency fund?",
  "answer_en": "An emergency fund is money set aside for unexpected costs like medical bills or repairs. Aim to save enough to cover three months of expenses.",
  "tags": ["savings", "emergency-fund", "basics"],
  "difficulty": "beginner"
}
```

**Rules for content:**

- `id` must be **unique** and never reused (format: `topic-NNN`).
- Write `answer_en` at a **low reading level** — short sentences, plain words, no jargon.
- Prefer **Ghana/West-Africa-relevant** examples (susu, MoMo, GHS, school fees).
- Keep answers **factually correct** — this is financial information people may act on.
- Add useful `tags` to help search find the entry.
- `difficulty` is one of `beginner`, `intermediate`, `advanced`.

After editing, validate the JSON is well-formed (see [Testing](#testing)).

---

## 2. Contribute Translations & Corpora (native speakers)

We are building the **first financial-domain parallel corpora** for Ghanaian languages. Even a few hundred validated sentence pairs are valuable and publishable.

1. Sentences must be **validated by a native or fluent speaker** — no machine-only translations.
2. Add pairs to the correct folder, e.g. [`data/corpora/parallel/en_tw/`](data/corpora/parallel/) as a `.tsv` (tab-separated) file.
3. Use the format:
   ```
   english_sentence	local_language_sentence	validated_by	date
   ```
4. Open a Pull Request with the language code in the title, e.g. `[en_tw] Add 30 savings sentence pairs`.

See [`data/corpora/README.md`](data/corpora/README.md) for the full folder layout.

---

## 3. Add a New Language

1. Add an entry to `LANGUAGES` in [`finling/languages/registry.py`](finling/languages/registry.py):

   ```python
   "ga": Language(
       code="ga",
       name="Ga",
       native_name="Gã",
       region="Greater Accra, Ghana",
       ghana_nlp_translation_model="<verified-huggingface-model-id-or-None>",
       supported=True,  # set True only when a translation model is wired up
   ),
   ```

2. Use the correct **ISO 639** language `code` so it matches GhanaNLP, HuggingFace, and other systems.
3. Only set `supported=True` once a real, working translation model is referenced. If no model exists yet, leave the model as `None` and `supported=False` — the language will still appear in the registry as "coming soon" without breaking the pipeline.
4. **Verify the model actually exists on HuggingFace** before referencing it. A broken model ID gives contributors a bad first experience.

---

## Development Setup

You need **Python 3.10+**.

```bash
# 1. Fork and clone the repo
git clone https://github.com/<your-username>/FinLing.git
cd FinLing

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Install in editable mode with dev tools
pip install -e ".[dev]"
```

Verify it works:

```bash
finling languages
finling query "What is savings?" --lang en
```

Run the API server:

```bash
python app.py
# docs at http://localhost:8000/docs
```

---

## Testing

Before opening a Pull Request, make sure everything passes locally:

```bash
# Run the test suite
pytest

# Lint and auto-fix style issues
ruff check . --fix

# Type-check
mypy finling
```

If you edited [`financial_concepts.json`](data/knowledge/financial_concepts.json), confirm it is valid JSON:

```bash
python -c "import json; json.load(open('data/knowledge/financial_concepts.json', encoding='utf-8')); print('valid JSON')"
```

All checks should be green. If you add a feature, please add a test for it under [`tests/`](tests/).

---

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b add-ga-language
   ```
2. **Make focused changes** — one logical change per PR. Smaller PRs get reviewed and merged faster.
3. **Run the checks** in [Testing](#testing) and make sure they pass.
4. **Write a clear PR title and description.** Explain *what* changed and *why*. Prefix language/content PRs with the area, e.g. `[en_tw]`, `[knowledge]`, `[lang]`.
5. **Link the issue** your PR addresses (e.g. "Closes #12").
6. A maintainer will review. Be ready to make small revisions — this is normal and collaborative.

### Commit messages

Keep them short and descriptive:

```
Add Ga language entry and 30 financial concepts
Fix translation fallback when model is missing
```

---

## Code Style

- Follow the existing structure — keep concerns separated (`languages`, `knowledge`, `pipeline`, `api`).
- `ruff` enforces formatting (88-char line length, Python 3.10 target). Run `ruff check . --fix` before committing.
- Add type hints to new Python code; `mypy` runs in CI.
- Don't add new runtime dependencies unless necessary, and mention why in your PR.

---

## Reporting Bugs & Suggesting Ideas

- **Bug:** Open a GitHub issue with steps to reproduce, what you expected, and what happened.
- **Idea / feature:** Open an issue describing the problem it solves before writing code, so we can align early.
- **Language or translation question:** Tag it clearly — we route these to native-speaker reviewers.

---

## Community & Conduct

FinLing is built with and for African language communities. Be respectful, assume good intent, and welcome newcomers — many contributors here are making their **first ever open source contribution**.

We especially welcome contributions from **GhanaNLP**, **NigerianNLP**, and the wider **AfricaNLP** community.

---

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
