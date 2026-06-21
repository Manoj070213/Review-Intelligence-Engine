# Review Intelligence Engine
### Turning unstructured customer reviews into product decisions with AI

A case study in building an LLM-powered pipeline that converts messy, free-text product reviews into structured, decision-ready intelligence.

---

## 1. The problem

Consumer brands generate **tens of thousands of product reviews** across Amazon, their own sites, and retail partners every month. Buried in that text is some of the most honest product feedback available: which products break, what customers wish existed, and where quality is slipping — often **weeks before** it shows up in return rates or warranty claims.

The problem is that this feedback is **unstructured and messy**. A human analyst can read a few hundred reviews; nobody can read 30,000. So the signal sits unused, and product and quality teams often learn about a defect trend only after returns spike.

**The question this project answers:** *Can unstructured reviews be automatically converted into structured, decision-ready intelligence — early enough to act on?*

---

## 2. Why it matters

- A defect trend caught a month late on a high-volume product can mean thousands of extra returns and a damaged rating that suppresses future sales.
- Feature requests scattered across reviews never reach the product team in aggregated form, so the next product cycle misses obvious wins.
- Manual review reading doesn't scale and is inconsistent between analysts.

The opportunity is an **always-on, automated** system that reads every review the day it's posted.

---

## 3. The solution — an AI pipeline

A five-stage pipeline that takes a raw review export and produces a decision dashboard:

| Stage | What happens | Tools |
|------|--------------|-------|
| 1. Ingest | Load raw reviews (CSV export / API) | Python, pandas |
| 2. Clean | Remove dupes, nulls, junk rows; normalize dates & ratings | pandas |
| 3. AI extraction | LLM reads each review → structured JSON: sentiment, themes, defect risk, return signal, feature request | Anthropic API, prompt engineering |
| 4. Aggregate | Load to SQL; compute scorecards, trends, complaint rankings | SQLite, SQL |
| 5. Visualize | Interactive dashboard for product & quality teams | HTML + Chart.js (BI-ready data export) |

The heart is **Stage 3**: a carefully engineered prompt that forces the model to return a **fixed JSON schema** with an enum list of themes, so the output is reliable enough to aggregate.

---

## 4. What the data showed (1,495 reviews, 6 Amazon products)

Run on the **Datafiniti "Consumer Reviews of Amazon Products"** dataset (real Amazon reviews of Fire tablets, Kindle, and AmazonBasics batteries):

- **The data is overwhelmingly positive** — 1,011 positive vs only 37 negative reviews (~68% positive). This is the honest reality of retail review data, and it matters: a naive "average sentiment" view would say everything is fine. The value is in finding the **small but concentrated negative signal**.
- **Defect risk isn't evenly spread.** The **Kindle E-reader (6.3%)** and **Fire HD 8 Tablet (3.9%)** carry the highest relative defect rates, while the batteries sit under 1.5%. That points a quality team to exactly where to look first — even though every product averages 4.4+ stars.
- **Durability is the #1 complaint theme and by far the #1 driver of defect signals** — a specific, actionable place to focus engineering attention.
- **Performance/speed and price-value** round out the top complaints, and **"kids usability"** surfaces as a defect theme tied to the kids' tablets — a product-line-specific insight that's invisible when reading reviews one by one.
- The monthly trend shows **defect-rate spikes reaching ~7%** in early-to-mid 2017 against an otherwise calm baseline — exactly the kind of blip an early-warning system exists to catch.

Each of these is an actionable finding — pulled automatically from text that averages 4.5 stars and looks fine on the surface.

---

## 5. The key engineering lesson: input quality drives output quality

The most important lesson in the project is that the **quality of an AI output is only as good as the quality of its input**:

- **v1 of the extraction prompt** let the model describe themes in free text. Result: dozens of slightly different labels for the same idea ("battery," "battery life," "charge doesn't last"). Aggregation was impossible — the output was technically correct but unusable.
- **v2 constrained the output** to a fixed JSON schema and a closed enum list of themes. Usable-output rate jumped substantially. The model never changed — **the structure of its input did.**
- A **hand-labeled validation set** measures sentiment accuracy on every run, so quality is a tracked number rather than an assumption. The rule-based fallback scores ~67% on tricky mixed-sentiment cases ("love the display, hate the storage limit") — which is precisely the argument for using the LLM: the model with a constrained prompt handles that nuance, while a keyword approach cannot.

That iteration loop — build, measure against ground truth, fix the input, re-measure — is the core of the whole project.

---

## 6. Skills demonstrated

- **Data visualization:** an interactive dashboard, plus a SQL layer that exports clean aggregate tables ready for any BI tool (Tableau, Power BI, Looker).
- **Building with AI:** a production-shaped LLM call with a schema-constrained prompt.
- **Real-world / messy data:** deliberately dirty input — dupes, nulls, mixed date formats, junk rows — handled in the cleaning stage.
- **SQL & Python:** Python for the pipeline, SQL for every business question.
- **Structured problem-solving:** a staged pipeline with a measured quality gate.

---

## 7. Where it could go next

- Swap the CSV ingest for a **live retailer API** so it runs daily.
- Add an **alerting layer**: auto-flag any product whose defect rate crosses a threshold and route it to the quality team.
- Add an **agentic step** that drafts a per-product summary memo for weekly product reviews — moving from dashboard to decision support.
- Re-validate the prompt against a fresh labeled set periodically to keep extraction quality honest as review language drifts.

---

*Pipeline: Datafiniti Amazon reviews CSV → Python clean → LLM extraction → SQL aggregation → dashboard.*
