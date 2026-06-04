# FinLing — Learning Guide for Founders & Presenters

> Use this document to understand **what** the code does, **why** it does it,
> and to test yourself before presenting to team members or contributors.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [pyproject.toml — Project Configuration](#2-pyprojecttoml)
3. [languages/registry.py — Language Registry](#3-languagesregistrypy)
4. [knowledge/base.py — Knowledge Base](#4-knowledgebasepy)
5. [data/knowledge/financial_concepts.json — Seed Data](#5-financial_conceptsjson)
6. [pipeline/core.py — The NLP Pipeline](#6-pipelinecorepy)
7. [api/routes.py — The Web API](#7-apiroutespy)
8. [cli.py — Command Line Interface](#8-clipy)
9. [app.py — Entry Point](#9-apppy)
10. [tests/ — Automated Tests](#10-tests)
11. [Master Q&A — Can You Present This?](#11-master-qa)
12. [Project Roadmap — Build in Public](#12-project-roadmap)

---

## 1. The Big Picture

### What the system does

A user types or speaks a financial question in their local language (e.g. Twi).
The system returns a clear, correct answer — in that same language.

### The pipeline in plain English

```
"Sika ho asɛm bɛn?" (Twi: "What about money?")
        ↓
    Detect: this is Twi
        ↓
    Translate to English: "What about money?"
        ↓
    Search knowledge base: find "savings", "budgeting", "loans" articles
        ↓
    Build a response in English
        ↓
    Translate response back to Twi
        ↓
    Return Twi response to user
```

### Why this architecture?

- **Language models work best in English** — most NLP research and training data is English-first. Working in English internally and translating at the edges is called the **"pivot language" strategy**.
- **Separation of concerns** — each layer (language, knowledge, pipeline, API) can be improved or replaced independently without breaking the others.
- **Low barrier for contributors** — a Twi speaker can contribute just by editing a JSON file. They don't need to know Python.

---

## 2. `pyproject.toml`

### What it is

The single configuration file for the entire Python project. It replaces older files like `setup.py`, `requirements.txt`, and `setup.cfg`.

### What it contains

| Section | Purpose |
|---|---|
| `[build-system]` | Tells Python *how* to package/install this project |
| `[project]` | Name, version, description, required Python version |
| `[project.dependencies]` | Libraries this project needs to run |
| `[project.optional-dependencies]` | Extra libraries only needed for development/testing |
| `[project.scripts]` | Creates the `finling` terminal command after install |

### Key dependencies explained

| Library | What it does in FinLing |
|---|---|
| `fastapi` | Builds the web API (the HTTP server) |
| `uvicorn` | Runs the FastAPI server (the engine behind it) |
| `transformers` | Loads GhanaNLP / Helsinki translation models |
| `sentence-transformers` | Converts text to numbers (vectors) for semantic search — Phase 2 |
| `langdetect` | Detects what language a piece of text is written in |
| `torch` | The math engine that runs neural network models |
| `pydantic` | Validates that API inputs are the right shape/type |
| `python-dotenv` | Loads secret keys from a `.env` file safely |

### Theory: Why `pyproject.toml` and not `requirements.txt`?

`requirements.txt` only lists packages. `pyproject.toml` also describes the project itself, how to build it, and how to install it as a reusable package. It is the modern Python standard (PEP 518, PEP 621).

---

## 3. `finling/languages/registry.py`

### What it does

Defines every language FinLing knows about — its code, name, region, and which AI translation model to use for it.

### Key concept: the `@dataclass`

```python
@dataclass(frozen=True)
class Language:
    code: str
    name: str
    ...
```

A **dataclass** is a Python class that automatically generates `__init__`, `__repr__`, and `__eq__` methods. `frozen=True` means the data cannot be changed after creation — languages are facts, not variables.

### Key concept: the `LANGUAGES` dictionary

```python
LANGUAGES: dict[str, Language] = {
    "tw": Language(code="tw", name="Twi (Akan)", ...),
    ...
}
```

This is a **lookup table** — given a language code like `"tw"`, you get back all the information about that language instantly. Dictionary lookups are O(1) — they are always fast, regardless of how many languages you add.

### Why `supported: bool`?

Languages are listed before they are fully ready. `supported=False` means "we know about this language but the pipeline isn't ready for it yet." This lets contributors see what needs to be done without breaking the running system.

### Theory: ISO 639 language codes

`"tw"` (Twi), `"ee"` (Ewe), `"ga"` (Ga) are **ISO 639-1/3** codes — international standards for naming languages. Using standards means your language codes will match codes used by GhanaNLP, HuggingFace, Google, and every other NLP system.

---

## 4. `finling/knowledge/base.py`

### What it does

Loads financial concept data from a JSON file and searches it using keyword matching.

### Key concept: `TypedDict`

```python
class Concept(TypedDict):
    id: str
    topic: str
    answer_en: str
    ...
```

A **TypedDict** tells Python (and your editor) exactly what keys a dictionary has and what type each value is. This catches bugs — if you try to access `concept["anwser_en"]` (typo), your editor will warn you.

### Key concept: The `search()` function

```python
score = sum(1 for term in query_terms if term in searchable)
```

This is **keyword search** — also called **bag-of-words** search. It:
1. Splits the query into individual words: `"what is savings"` → `["what", "is", "savings"]`
2. Counts how many of those words appear in each concept's text
3. Returns the concepts with the highest counts

### Why keyword search first and not a vector database?

| Approach | Pros | Cons |
|---|---|---|
| Keyword search (Phase 1) | No setup, no GPU, instant, auditable | Misses synonyms, order-blind |
| Vector/semantic search (Phase 2) | Understands meaning, handles synonyms | Needs embeddings model, more complex |

Starting simple lets you validate the idea before investing in infrastructure. The `search()` function signature will not change when you upgrade to vector search — only the internals will.

### Theory: Information Retrieval

FinLing's knowledge base is a tiny **Information Retrieval (IR)** system. The full version of this idea powers Google Search. The academic field is called IR, and the progression is:
1. Keyword/BM25 → 2. TF-IDF → 3. Dense retrieval (vectors) → 4. RAG (Retrieval-Augmented Generation)

---

## 5. `data/knowledge/financial_concepts.json`

### What it is

The **knowledge base** — the ground truth that FinLing answers from. Every answer the system gives comes from here.

### Structure of one entry

```json
{
  "id": "savings-001",
  "topic": "savings",
  "subtopic": "what_is_savings",
  "question_en": "What is savings?",
  "answer_en": "Savings is money you keep aside...",
  "tags": ["savings", "basics", "emergency-fund"],
  "difficulty": "beginner"
}
```

| Field | Purpose |
|---|---|
| `id` | Unique identifier — never changes, used to reference content |
| `topic` | Broad category for filtering and navigation |
| `question_en` | The canonical question this entry answers |
| `answer_en` | The answer — written at a low reading level on purpose |
| `tags` | Extra keywords to improve search recall |
| `difficulty` | Helps future UI decide what to show first-time users |

### Why JSON and not a database?

JSON files can be edited by anyone with a text editor, committed to Git, reviewed in pull requests, and understood without a database degree. For Phase 1, this is the right choice. Phase 2 will load this into SQLite or a vector database.

### Theory: Knowledge Representation

Storing knowledge as structured data (rather than raw text) is a fundamental NLP design decision. Structured data is:
- **Auditable** — you can read every fact the system knows
- **Correctable** — wrong answer? Edit the JSON, no model retraining
- **Attributable** — you can cite where each answer came from

---

## 6. `finling/pipeline/core.py`

### What it does

This is the brain. It orchestrates the full journey from a user's question to their answer.

### Key concept: The `FinLingPipeline` class

A **class** is used here (rather than standalone functions) because the pipeline has **state** — it caches loaded translation models in `self._translators` so they are not reloaded on every query. Loading a model takes ~5 seconds; caching means it only happens once.

### Key concept: Lazy loading

```python
def _get_translator(self, lang_code, direction):
    if cache_key in self._translators:
        return self._translators[cache_key]   # already loaded, return instantly
    # ... load it now ...
```

**Lazy loading** means: don't load something until you actually need it. The alternative (eager loading at startup) would make the server take 30+ seconds to start.

### Key concept: The `QueryResult` dataclass

```python
@dataclass
class QueryResult:
    original_query: str
    detected_language: str
    english_query: str
    ...
```

Instead of returning a raw dictionary (where keys can be misspelled), a dataclass gives you a typed, documented return value. Every caller knows exactly what fields to expect.

### Key concept: The pivot language strategy

```
Twi input → translate to English → process in English → translate back to Twi
```

This is used by Google Translate, DeepL, and most multilingual NLP systems. English is the **pivot** because:
- More training data exists in English than any other language
- Most financial terminology was standardised in English
- One English knowledge base serves all languages — you don't write 10 separate knowledge bases

### Key concept: Graceful degradation

```python
if translator is None:
    logger.warning("No translation model for '%s'. Using original text.", lang_code)
    return text
```

If a translation model is missing, the system keeps working — it just returns the English text instead of crashing. This is called **graceful degradation**. For an open source project where languages are added incrementally, this is critical.

### Theory: NLP Pipeline Design

Every serious NLP system is a **pipeline** — a sequence of stages where the output of one stage feeds the next. The stages in FinLing mirror industry-standard NLP system design:

```
Input → Preprocessing → Understanding → Retrieval → Generation → Output
```

FinLing's stages:
```
Raw text → Language detect → Translation → Search → Response build → Translation → Answer
```

---

## 7. `finling/api/routes.py`

### What it does

Exposes FinLing's pipeline over HTTP so any application (web, mobile, WhatsApp bot) can use it.

### Key concept: FastAPI

FastAPI automatically:
- Validates incoming requests against your Pydantic schemas
- Returns clear error messages for invalid inputs
- Generates interactive documentation at `/docs`
- Is asynchronous — handles many users at once without blocking

### Key concept: Pydantic schemas

```python
class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    lang_code: str | None = Field(None, ...)
```

**Pydantic** is a data validation library. `min_length=1` means empty strings are rejected before they reach your pipeline. `max_length=1000` prevents abuse (someone sending a 10MB string). This is **input validation** — one of the OWASP Top 10 security practices.

### The three endpoints

| Endpoint | Method | What it does |
|---|---|---|
| `/` | GET | Health check — tells you the server is alive |
| `/languages` | GET | Lists all supported languages |
| `/query` | POST | Takes a question, returns an answer |

### Theory: REST API design

REST (Representational State Transfer) is a convention for how web services communicate. Key rules:
- **GET** = read data (safe, repeatable)
- **POST** = send data for processing
- Resources are nouns (`/languages`, `/query`), not verbs (`/getLanguages`)

---

## 8. `finling/cli.py`

### What it does

Lets developers and testers use FinLing from the terminal without running a server:

```bash
finling query "What is savings?" --lang en
finling languages
```

### Key concept: `argparse`

Python's built-in library for building command-line interfaces. It:
- Parses `sys.argv` (the list of words typed after the command)
- Generates `--help` documentation automatically
- Validates that required arguments are provided

### Why build a CLI at all?

- **Testing without a browser** — fastest way to check the pipeline works
- **Scriptable** — other programs can call FinLing in shell scripts
- **Demoing** — running a live demo in a terminal is often more convincing than showing a UI

---

## 9. `app.py`

### What it does

The single file you run to start the whole system:

```python
uvicorn.run("finling.api.routes:app", host="0.0.0.0", port=8000, reload=True)
```

### Key concept: `uvicorn`

Uvicorn is an **ASGI server** — it sits between the internet and your FastAPI app, handling raw HTTP connections and passing them to your code. Think of it as the engine that powers the car (FastAPI is the car).

### Key concept: `reload=True`

During development, `reload=True` watches your files and restarts the server automatically when you save a change. Turn this OFF in production.

### Key concept: `host="0.0.0.0"`

`0.0.0.0` means "listen on all network interfaces" — not just your own machine. This is needed when running inside Docker or on a cloud server so external traffic can reach it.

---

## 10. `tests/`

### What they do

Automated tests verify that your code behaves correctly. Run all tests with:

```bash
pytest
```

### Key concept: `pytest`

Python's most popular testing framework. Each function that starts with `test_` is automatically discovered and run.

### Key concept: `assert`

```python
assert len(concepts) > 0
```

If the condition is False, the test fails and pytest tells you exactly which assertion failed. This is how you catch regressions — when a change breaks something that used to work.

### Theory: Why test?

- **Confidence** — you can refactor code and know immediately if you broke something
- **Documentation** — tests show exactly how a function is expected to behave
- **Open source trust** — contributors are more comfortable submitting code when tests exist

---

## 11. Master Q&A — Can You Present This?

Test yourself. Cover the answer, read the question, then check.

---

### Section A — Architecture

**Q1. In one sentence, what does FinLing do?**
> FinLing answers financial questions in African local languages by translating queries to English, searching a curated knowledge base, and translating the answer back.

**Q2. What is the "pivot language" strategy and why does FinLing use it?**
> Using a common intermediate language (English) for all internal processing. FinLing uses it because most NLP models are English-first, and one English knowledge base can serve all supported languages.

**Q3. Why is the pipeline split into separate modules (languages, knowledge, pipeline, api)?**
> Separation of concerns — each layer can be improved, replaced, or contributed to independently. A Twi linguist doesn't need to understand FastAPI to add language content.

**Q4. What would you change to add support for Yoruba?**
> Add a `Language` entry in `registry.py` with the correct model ID, set `supported=True`, and add Yoruba-language knowledge entries to the JSON. No pipeline code changes needed.

---

### Section B — NLP Concepts

**Q5. What is language detection and why might it fail for Twi?**
> Language detection uses statistical patterns to identify a language. It can fail for Twi because `langdetect` was not trained on Twi — low-resource languages often get misidentified. FinLing allows users to explicitly pass `lang_code` to bypass detection.

**Q6. What is the difference between keyword search and semantic (vector) search?**
> Keyword search counts exact word matches. Semantic search converts text to numerical vectors and finds conceptually similar content — it understands that "save money" and "accumulate funds" mean the same thing. FinLing starts with keyword search and upgrades later.

**Q7. What is RAG and how does FinLing relate to it?**
> Retrieval-Augmented Generation — instead of an LLM generating an answer from memory, it first retrieves relevant documents and uses them as context. FinLing's `search() → _build_response()` flow is the retrieval half of RAG. Adding an LLM to the response step would complete the pattern.

**Q8. What is a translation model and where do FinLing's come from?**
> A neural network trained on parallel text (same sentences in two languages) to learn translation. FinLing uses Helsinki-NLP's `opus-mt` models, some of which have been fine-tuned by GhanaNLP on Ghanaian language data.

---

### Section C — Python & Engineering

**Q9. What does `frozen=True` in a dataclass mean and why is it used for `Language`?**
> The object cannot be modified after creation. `Language` represents a fact (a language exists), not a mutable state. Immutability prevents bugs where language metadata is accidentally changed at runtime.

**Q10. What is lazy loading and where is it used in FinLing?**
> Loading a resource only when it is first needed. Used in `_get_translator()` — translation models (which are large) are only loaded when a query in that language is first received, keeping startup fast.

**Q11. Why does `search()` use `top_k` as a parameter instead of always returning all results?**
> Returning all results would overwhelm users. `top_k` gives callers control over how many results they want. This is a common API design pattern — callers know their context better than the function does.

**Q12. What is Pydantic and why is input validation important?**
> Pydantic validates that incoming data matches an expected structure and type. Input validation prevents crashes, incorrect behaviour, and security vulnerabilities (OWASP A03: Injection) from malformed user input.

---

### Section D — Open Source & Community

**Q13. How would you explain this project to a GhanaNLP contributor in one paragraph?**
> FinLing is an open source project that makes financial education accessible in Ghanaian and West African local languages. We use GhanaNLP's translation models at the core. Contributors can add language support, improve translations, or expand the financial knowledge base. The codebase is structured so language experts don't need deep Python knowledge to contribute.

**Q14. Why MIT licence?**
> MIT is the most permissive common open source licence. Contributors and companies can use, modify, and distribute the code freely — even in commercial products — with no restrictions beyond attribution. This maximises adoption.

**Q15. What is the `data/` folder for and why is it separate from `finling/`?**
> `data/` holds content (knowledge base, future corpora, model configs). `finling/` holds code. Separating them means content contributors never need to touch Python files, and the data can be versioned separately (e.g. with DVC).

---

*You are ready to present when you can answer all 15 questions without checking.*

---

## 12. Project Roadmap — Build in Public

---

### Phase 0 — Foundation ✅ *(Done)*

| Task | Status |
|---|---|
| Define the problem and mission | ✅ |
| Choose project name (`FinLing`) | ✅ |
| Create GitHub repository with topics | ✅ |
| Scaffold project structure | ✅ |
| Language registry (Twi, Ga, Ewe, Dagbani, Yoruba, Igbo) | ✅ |
| Seed financial knowledge base (8 concepts) | ✅ |
| NLP pipeline skeleton (detect → translate → search → respond) | ✅ |
| FastAPI endpoints (`/`, `/languages`, `/query`) | ✅ |
| CLI (`finling query`, `finling languages`) | ✅ |
| Automated tests | ✅ |

---

### Phase 1 — Go Live Online *(This Week)*

| Task | Status |
|---|---|
| Purchase `finling.org` (Cloudflare Registrar ~$9/yr) | ⬜ |
| Point `finling.org` → GitHub repo (temporary redirect) | ⬜ |
| Create HuggingFace organization: `FinLing` | ⬜ |
| Post "the why" thread on Twitter/X tagging `@GhanaNLP` | ⬜ |
| Introduce project in GhanaNLP Discord/community | ⬜ |
| Write `CONTRIBUTING.md` with language contribution guide | ⬜ |
| Add "good first issue" labels on GitHub | ⬜ |

> **Domain note:** `.org` is the right choice for an open source community project.
> Buy now — it is cheap insurance and won't be available forever.

---

### Phase 2 — First Working Demo *(Weeks 2–4)*

| Task | Status |
|---|---|
| Install dependencies and run pipeline end-to-end in English | ⬜ |
| Integrate GhanaNLP Twi translation model (`opus-mt-tw-en`) | ⬜ |
| Test full loop: Twi query → English → answer → Twi response | ⬜ |
| Expand knowledge base to 30+ concepts | ⬜ |
| Record short demo video (CLI or API responding in Twi) | ⬜ |
| Post demo on Twitter + LinkedIn | ⬜ |

---

### Phase 3 — Community & Contributors *(Month 2)*

| Task | Status |
|---|---|
| Publish on HuggingFace Spaces (free hosted demo) | ⬜ |
| Activate Ga language support | ⬜ |
| Activate Ewe language support | ⬜ |
| Reach out to NigerianNLP for Yoruba contribution | ⬜ |
| Add WhatsApp bot interface (Twilio or Meta Cloud API) | ⬜ |
| First external contributor merged PR | ⬜ |
| LinkedIn post: project story + mission | ⬜ |

---

### Phase 4 — Semantic Intelligence *(Month 3–4)*

| Task | Status |
|---|---|
| Replace keyword search with vector/semantic search | ⬜ |
| Add `sentence-transformers` embedding pipeline | ⬜ |
| Migrate knowledge base to SQLite or ChromaDB | ⬜ |
| Evaluate adding a small LLM (Llama 3 / Gemma) for response generation | ⬜ |
| Add speech-to-text input (GhanaNLP Whisper model) | ⬜ |

---

### Phase 5 — Scale & Reach *(Month 5+)*

| Task | Status |
|---|---|
| Build `finling.org` website (landing page + live demo) | ⬜ |
| USSD interface (feature phones, no internet required) | ⬜ |
| Partner with Bank of Ghana / financial literacy NGOs for content | ⬜ |
| Apply to open source grants (Mozilla, Lacuna Fund, Google.org) | ⬜ |
| Support 5+ languages | ⬜ |

---

### Build in Public — What to Post & Where

#### Twitter/X post types

| Type | Example |
|---|---|
| **The why** | *"Millions of Ghanaians make financial decisions without clear info in their own language. FinLing is fixing that — financial intelligence in Twi, Ga, Ewe, and more. 🧵"* |
| **Behind the decision** | *"Why did we name it FinLing? Finance + Linguistics. The fusion that doesn't exist in African tech yet."* |
| **Show it working** | Screen recording of `finling query` returning a Twi answer |
| **The problem you hit** | *"Langdetect misidentifies Twi. Here's how we're solving it 👇"* |
| **Community call** | *"We need Twi speakers to review our financial translations. Reply if you can help."* |
| **Milestones** | First commit. First star. First contributor. First Twi response. Screenshot each one. |
| **Tag always** | `@GhanaNLP` · `#BuildInPublic` · `#AfricaNLP` · `#GhTech` · `#NigerianNLP` |

#### Platform strategy

| Platform | Action |
|---|---|
| **GitHub** | Pin repo · write `CONTRIBUTING.md` · add "good first issue" labels |
| **Twitter/X** | Short punchy posts — thinking, demos, milestones |
| **LinkedIn** | Longer mission-driven posts — target fintech, African tech, NLP professionals |
| **HuggingFace** | Create `FinLing` org · host models and datasets · where NLP contributors look |
| **Discord** | Join GhanaNLP community first — introduce there before any public launch |

#### Launch sequence

```
Step 1 → Buy finling.org, point to GitHub                (today)
Step 2 → Post the "why" thread on Twitter                (this week)
Step 3 → Introduce in GhanaNLP Discord                   (this week)
Step 4 → Create FinLing org on HuggingFace               (next week)
Step 5 → Record and post first working demo video        (end of Phase 2)
Step 6 → Public launch post tagging GhanaNLP             (after demo)
```
