# EX YU Music Analysis

*[Srpska verzija / Serbian version: [README.md](README.md)]*

Technical implementation of the AI/NLP component of a master's thesis in Artificial
Intelligence: **"Analysing changing trends in ex-Yugoslav music using LLM models"**
(University of Belgrade, Faculty of Organisational Sciences)

The project analyses thematic, linguistic and value-related transformations in the
lyrics of ex-Yugoslav popular music across three historical periods:

| Period | Years |
|---|---|
| Socialist Yugoslavia (SFRY) | 1960–1991 |
| Transition | 1991–2005 |
| Contemporary | 2005–present |

It combines classical NLP methods (topic modelling, sentiment analysis, NER) with
LLM-based analysis (Claude API) for deeper interpretation of the content.

> **Status**: Phases 1–6 complete — the full pipeline is finished. Collection
> (4,113 songs) → preprocessing (4,084 analysis-ready) → NLP analysis (TF-IDF,
> LDA, BERTopic, sentiment, lexical diversity) → LLM validation
> (gold standard n=299, Cohen's kappa: theme=0.405, emotion=0.356) →
> visualisations (word clouds, trend plots, heatmaps, per-decade views).
> Interactive overview of all findings: `notebooks/finalni_pregled.ipynb`.
> Detailed documentation in `docs/`.

## Project structure

```
ex-yu-music-analysis/
├── config/
│   └── config.py          # periods, genres, paths, LLM/scraping settings
├── data/
│   ├── raw/                # raw collected lyrics (NOT on GitHub)
│   ├── processed/          # cleaned dataset (NOT on GitHub)
│   └── gold_standard/      # manually annotated sample used for validation
├── docs/
│   ├── napredak_projekta.md    # detailed progress report across all phases
│   └── obrasci_neslaganja.md   # analysis of LLM/gold-standard disagreement patterns
├── src/
│   ├── scraping/           # lyrics collection from lyrics sites
│   ├── preprocessing/      # cleaning, normalisation, lemmatisation
│   ├── nlp/                # topic modelling, sentiment, NER, TF-IDF
│   ├── llm/                # Claude API analysis + prompt templates
│   ├── visualization/      # plots and word clouds
│   └── utils/              # shared helpers (schema, etc.)
├── notebooks/               # Jupyter notebooks with the analysis
│   └── finalni_pregled.ipynb   # interactive overview of all findings, for the defence
├── results/
│   ├── figures/             # generated plots
│   └── reports/             # result tables and reports
└── tests/
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env          # then enter your ANTHROPIC_API_KEY
```

## Why the raw lyrics are not on GitHub

Song lyrics are protected by copyright. What goes on GitHub is the code, the
metadata (artist / year / genre) and the aggregated results of the analysis —
never the lyrics themselves.

## Known limitations (as of Phase 5)

- **The trap genre is under-represented** (8 songs out of 4,113 in the corpus).
  The main source (tekstovi-pjesama.com) has almost no trap artists (Coby,
  Voyage, Jala Brat, Buba Corelli and Nucci were not found). Genius.com was
  evaluated and rejected (insufficient regional coverage). lyricstranslate.com
  does have the content but blocks automated requests (bot detection), which
  would need to be resolved before it could be used. **Deferred to a later
  phase**, and documented as a limitation in line with the methodology set out
  in section 4.6 of the thesis proposal.
- Several well-known SFRY rock and new-wave artists are likewise missing from
  the main source (Riblja Čorba, Šarlo Akrobata, Film, Bajaga i Instruktori and
  others) — same cause.
- Roughly 29 songs turned out to be in a foreign language (English, German) —
  versions recorded for foreign markets (e.g. Zdravko Čolić, Dragana Mirković).
  These were removed automatically from the analysis-ready corpus (fewer than
  10 lemmas after lemmatisation is a reliable signal that the text is not in an
  ex-Yugoslav language).
- NER (named-entity recognition) produces unreliable, fragmented results because
  of a version mismatch: the classla library was tested against torch 1.12.0,
  while the version available for Python 3.13 is torch 2.6.0+ (a gap of roughly
  three years of development). The entity-extraction code is written and
  functional (`src/nlp/run_ner.py`), but its output is not reliable enough to
  analyse, so NER is excluded from the final findings of the thesis. Downgrading
  torch is not possible on Python 3.13 (no compatible packages below 2.6.0).
- The free tier of the Google Gemini API proved considerably more restrictive
  than documented (~20 requests/day rather than ~1,500, following a change in
  late 2025), so the project moved to the Anthropic Claude API — paid, but
  inexpensive at this scale (~$0.50).
- LLM classification (theme / emotion / values) was carried out on the gold
  standard sample (n=299) rather than the full corpus (n=4,084). This was a
  methodological decision: the same sample also serves as the validation set,
  which avoids unnecessary cost and time on the full corpus without a
  measurable gain in the reliability of the findings.
- LLM classification shows a systematic bias towards dominant categories and is
  weaker at recognising genre-specific and culturally specific nuance (satire,
  the conventions of folk-music expression, hedonism vs. love). This is
  documented in detail in `docs/obrasci_neslaganja.md`.
- **Per-decade analysis should be interpreted with caution.** The decade column
  is derived from a single estimated year per artist rather than the actual year
  of each song, so some decades (particularly the 2000s, n=271) have an uneven
  genre composition that can look like a "trend" when it is in fact an artefact
  of sampling (see the note on `results/figures/mattr_by_decade.png`).
