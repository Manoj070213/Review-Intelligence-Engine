# Review Intelligence Engine

An end-to-end data pipeline that turns thousands of messy, unstructured consumer-product reviews into structured, decision-ready intelligence — sentiment, complaint themes, defect risk, and feature requests — using a large language model.

Retailers and product teams collect huge volumes of review text but rarely mine it at scale. A single analyst can read a few hundred reviews; nobody can read tens of thousands. This project automates that reading: every review is parsed into structured fields that can be aggregated, trended, and turned into action — surfacing quality problems and feature requests that would otherwise stay buried in free text.

## What it does

```
Raw reviews  →  clean  →  LLM extraction  →  SQL aggregation  →  interactive dashboard
```

For each review, an LLM returns a structured JSON record (sentiment, themes, defect risk, return signal, feature request). The records are loaded into SQLite, aggregated with SQL into product scorecards and monthly trends, and visualized in a self-contained HTML dashboard.

## Dataset

Built on the public **Datafiniti "Consumer Reviews of Amazon Products"** dataset — ~28,000 real Amazon reviews covering Fire tablets, Kindle e-readers, and AmazonBasics batteries. The pipeline focuses on the six highest-volume products and analyzes a 1,495-review working sample.

The full source CSV (~265 MB) is not included in this repo due to size. Download it from [Kaggle](https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products), place it at `data/amazon_reviews_real.csv`, and the pipeline will regenerate everything. The processed sample (`data/raw_reviews.csv`) is included so the pipeline runs immediately from step 2 without the download.

## Run it

```bash
pip install pandas anthropic

python src/01_load_real_data.py     # load source reviews, map to pipeline schema
python src/02_clean_and_extract.py  # clean messy data + LLM extraction
python src/03_sql_analysis.py       # load SQLite, run aggregation queries
python src/04_validate.py           # measure extraction accuracy vs labeled set
# then open output/dashboard.html in a browser
```

## How the extraction works

The core of the project is the prompt in `build_prompt()` (in `src/02_clean_and_extract.py`). It constrains the model to return a **fixed JSON schema** with a **closed list of theme labels**, rather than free-text analysis.

This constraint is the most important design decision in the project. An early version let the model describe themes in its own words, which produced dozens of near-duplicate labels ("battery," "battery life," "charge issues") that could not be aggregated. Locking the output to a defined schema and enum made the results countable and trendable — the model didn't change, the structure of its input did.

Extraction accuracy is measured against a hand-labeled validation set in `04_validate.py`, so output quality is a tracked metric rather than an assumption.

## Using a real LLM vs. the offline fallback

The extraction step auto-detects an Anthropic API key. With a key set, it calls the real model:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

python src/02_clean_and_extract.py
```

Without a key, it falls back to a transparent rule-based extractor so the full pipeline still runs offline. The fallback handles clear-cut reviews well but misses nuance (e.g. mixed sentiment like "love the display, hate the storage limit"), which is exactly where the LLM adds value.

## Key findings (1,495-review sample)

- Reviews skew strongly positive (~68%), so the value is in isolating the small, concentrated negative signal rather than reading the average.
- Defect risk concentrates in specific products (Kindle and Fire HD 8) even though every product averages 4.4+ stars.
- **Durability** is the top complaint theme and the leading driver of defect signals.
- Monthly defect-rate spikes to ~7% in early 2017 against an otherwise calm baseline — the kind of early-warning blip the system is designed to catch.

## Tech stack

Python (pandas) · Anthropic API · SQLite / SQL · HTML + Chart.js dashboard

## Files

- `src/01_load_real_data.py` — load source reviews into the pipeline schema
- `src/01_generate_data.py` — synthetic data generator (runs with no external dataset)
- `src/02_clean_and_extract.py` — data cleaning + LLM extraction (the core)
- `src/03_sql_analysis.py` — SQL aggregation and business queries
- `src/04_validate.py` — accuracy measurement vs. a labeled set
- `output/dashboard.html` — interactive dashboard
- `output/dashboard_data.json` — aggregated tables (ready for any BI tool)
