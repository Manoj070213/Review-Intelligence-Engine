# Review Intelligence Engine

Turn messy consumer-product reviews into structured, decision-ready intelligence using an LLM. Built around the SharkNinja Data/AI Analyst role.

## What it does
Raw reviews → clean → **LLM extraction** (sentiment, themes, defect risk, feature requests) → SQL aggregation → interactive dashboard.

## Run it
```bash
pip install pandas anthropic
python src/01_load_real_data.py     # loads real Amazon reviews, maps to pipeline schema
python src/02_clean_and_extract.py  # cleans + runs AI extraction
python src/03_sql_analysis.py       # loads SQLite, runs business queries
python src/04_validate.py           # measures sentiment accuracy vs gold set
# open output/dashboard.html in a browser
```

The pipeline runs on the real **Datafiniti "Consumer Reviews of Amazon Products"**
dataset (Fire tablets, Kindle, AmazonBasics batteries). The source CSV lives at
`data/amazon_reviews_real.csv`. `01_load_real_data.py` samples 1,500 reviews from
the top 6 products and maps the Datafiniti columns into the schema the rest of the
pipeline expects — bump `SAMPLE_N` in that file to run more.

> Note: if you regenerate from scratch, `src/01_generate_data.py` (the original
> synthetic generator) is still included as a fallback that needs no dataset.

## Using the REAL Claude API
The extraction step auto-detects an API key. With no key it runs a transparent
rule-based simulator so the pipeline works end-to-end. To use the real model:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python src/02_clean_and_extract.py
```

The exact production prompt is in `build_prompt()` in `src/02_clean_and_extract.py`
— this is what you walk an interviewer through. It forces a fixed JSON schema and a
closed list of theme labels, which is the key to making the output aggregatable.

## Files
- `src/01_load_real_data.py` — loads real Datafiniti Amazon reviews into the pipeline schema
- `src/01_generate_data.py` — synthetic fallback generator (no dataset needed)
- `src/02_clean_and_extract.py` — cleaning + LLM extraction (the core)
- `src/03_sql_analysis.py` — SQL business-question layer
- `src/04_validate.py` — accuracy measurement vs hand-labeled gold set
- `output/dashboard.html` — interactive dashboard (open in browser)
- `output/BUSINESS_CASE.md` — the full business narrative for the interview
- `output/dashboard_data.json` — aggregated tables (drop into Tableau/Power BI)
- `data/amazon_reviews_real.csv` — the source dataset

## The interview story in one line
"I built a pipeline that reads every product review, flags defect risk and feature
requests automatically, and surfaces it on a dashboard — and the hardest, most
valuable part was learning that constraining the model's INPUT (a schema-locked
prompt) is what made the OUTPUT usable, which I proved by measuring accuracy against
a hand-labeled set."
