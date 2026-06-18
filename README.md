# FinLing

> **Financial intelligence in African languages — starting with Ghana**

Built by and for African language communities. FinLing makes financial education accessible to people who speak Twi, Ga, Ewe, Dagbani, Yoruba, Igbo, and more — in their own language.

---

## Why FinLing?

Most financial tools and education content are English-only. Millions of people across Ghana and West Africa make financial decisions without access to clear, reliable information in their mother tongue. FinLing bridges that gap using NLP.

---

## Architecture (Layer by Layer)

```
User query (local language)
    → Language detection
    → Translate to English        (GhanaNLP / Helsinki-NLP models)
    → Search financial knowledge base
    → Build response
    → Translate back to local language
    → Return to user
```

---

## Project Structure

```
FinLing/
├── app.py                        # Server entry point
├── pyproject.toml                # Project config & dependencies
├── finling/
│   ├── api/
│   │   └── routes.py             # FastAPI endpoints
│   ├── cli.py                    # Command-line interface
│   ├── knowledge/
│   │   └── base.py               # Financial knowledge base loader & search
│   ├── languages/
│   │   └── registry.py           # Language registry (codes, models, metadata)
│   └── pipeline/
│       └── core.py               # Main NLP query pipeline
├── data/
│   └── knowledge/
│       └── financial_concepts.json   # Seed knowledge base
└── tests/
    ├── test_knowledge_base.py
    └── test_languages.py
```

---

## Supported Languages

| Code | Language | Region | Status |
|------|----------|--------|--------|
| `tw` | Twi (Akan) | Ashanti, Eastern, Central Ghana | Active |
| `ga` | Ga | Greater Accra | Coming soon |
| `ee` | Ewe | Volta Region | Coming soon |
| `dag` | Dagbani | Northern Region | Coming soon |
| `yo` | Yoruba | Nigeria | Planned |
| `ig` | Igbo | Nigeria | Planned |

---

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Run the API server
python app.py

# Or use the CLI
finling query "What is savings?" --lang en
finling languages
```

API docs available at `http://localhost:8000/docs` after starting the server.

---

## Contributing

We welcome contributions from GhanaNLP, NigerianNLP, and all African NLP communities.

- **Add a language:** Create an entry in `finling/languages/registry.py`
- **Add financial content:** Add entries to `data/knowledge/financial_concepts.json`
- **Improve translation:** Fine-tune or replace models in `finling/pipeline/core.py`

See `CONTRIBUTING.md` for guidelines.

---

## License

MIT — free to use, modify, and distribute.

