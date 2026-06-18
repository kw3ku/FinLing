# FinLing Corpora

This folder holds all language data used to train, fine-tune, and evaluate FinLing's NLP models.

## Structure

```
corpora/
├── parallel/
│   └── en_tw/        English-Twi sentence pairs (financial domain)
│   └── en_ga/        English-Ga sentence pairs
│   └── en_ee/        English-Ewe sentence pairs
│   └── en_dag/       English-Dagbani sentence pairs
└── monolingual/
    └── tw/           Raw Twi financial text
    └── ga/           Raw Ga financial text
    └── ee/           Raw Ewe financial text
    └── dag/          Raw Dagbani financial text
```

## How to Contribute

1. Native speaker validates each sentence — no machine-only translations
2. Add sentence pairs to the correct `parallel/en_{code}/` folder as `.tsv` (tab-separated)
3. Format: `english_sentence\tlocal_language_sentence\tvalidated_by\tdate`
4. Open a Pull Request with the language code in the title

## Why This Matters

No financial domain corpora exist in Twi, Ga, Ewe, or Dagbani.
Even 500 validated sentence pairs covering savings, loans, and mobile money
would be the first of their kind — and publishable at AfricaNLP or EMNLP.
