# Review Intelligence Engine
### Turning messy customer reviews into product decisions with AI

**A portfolio project built around the SharkNinja Data/AI Analyst role**

---

## 1. The business problem

Consumer-appliance brands like SharkNinja generate **tens of thousands of product reviews** across Amazon, their own site, and retail partners every month. Buried in that text is the company's most honest product feedback: which products break, what customers wish existed, and where quality is slipping — often **weeks before** it shows up in return rates or warranty claims.

The problem is that this feedback is **unstructured and messy**. A human analyst can read a few hundred reviews; nobody can read 30,000. So the signal sits unused, and product and quality teams find out about a defect trend only after returns spike.

**The question this project answers:** *Can we automatically convert raw, unstructured reviews into structured, decision-ready intelligence — and catch quality problems early?*

---

## 2. The cost of doing nothing

- A defect trend caught one month late on a high-volume SKU can mean **thousands of extra returns** and a dented product rating that suppresses future sales.
- Feature requests scattered across reviews never reach the product team in aggregated form, so the next product cycle misses obvious wins.
- Manual review reading doesn't scale and is inconsistent between analysts.

The opportunity is an **always-on, automated** system that reads every review the day it's posted.

---

## 3. The solution — an AI pipeline

A five-stage pipeline that takes a raw review export and produces a live decision dashboard:

| Stage | What happens | Tools |
|------|--------------|-------|
| 1. Ingest | Pull raw reviews (CSV export / API) | Python, pandas |
| 2. Clean | Remove dupes, nulls, junk rows; normalize dates & ratings | pandas |
| 3. **AI extraction** | LLM reads each review → structured JSON: sentiment, themes, **defect risk**, return signal, feature request | **Claude API, prompt engineering** |
| 4. Aggregate | Load to SQL; compute scorecards, trends, complaint rankings | SQLite, SQL |
| 5. Visualize | Interactive dashboard for product & quality teams | Dashboard / Tableau-Power BI-ready data |

The heart is **Stage 3**: a carefully engineered prompt that forces the model to return a **fixed JSON schema** with an enum list of themes, so the output is reliable enough to aggregate.

---

## 4. What the data showed (real data: 1,495 reviews, 6 Amazon products)

Run on the **Datafiniti "Consumer Reviews of Amazon Products"** dataset (real Amazon reviews of Fire tablets, Kindle, and AmazonBasics batteries):

- **The data is overwhelmingly positive** — 1,011 positive vs only 37 negative reviews (a ~68% positive share). This is the honest reality of retail review data, and it matters: a naive "average sentiment" view would say everything is fine. The value is in finding the **small but concentrated negative signal**.
- **Defect risk isn't evenly spread.** The **Kindle E-reader (6.3%)** and **Fire HD 8 Tablet (3.9%)** carry the highest relative defect rates, while the batteries sit under 1.5%. That tells a quality team exactly where to look first — even though every product averages 4.4+ stars.
- **Durability is the #1 complaint theme and by far the #1 driver of defect signals** — a specific, actionable place to focus engineering attention.
- **Performance/speed and price-value** round out the top complaints, and **"kids usability"** surfaces as a defect theme tied to the Fire Kids tablets — a product-line-specific insight you'd never spot reading reviews one by one.
- The monthly trend shows **defect-rate spikes reaching ~7%** in early-to-mid 2017 against an otherwise calm baseline — exactly the kind of blip this early-warning system exists to catch.

Every one of these is a decision a real product or quality manager could act on this week — pulled automatically from text that averages 4.5 stars and looks fine on the surface.

---

## 5. "The quality of an AI output is only as good as the input"

This is a SharkNinja success driver, and it's the most important engineering lesson in the project:

- **v1 of the extraction prompt** let the model describe themes in free text. Result: 40+ slightly different labels for the same idea ("battery," "battery life," "charge doesn't last"). Aggregation was impossible — the output was technically correct but **useless**.
- **v2 constrained the output** to a fixed JSON schema and a closed enum list of themes. Usable-output rate jumped from roughly **70% to over 90%**. The model never changed — **the input did.**
- I built a **gold validation set** of hand-labeled reviews and measure sentiment accuracy against it on every run, so quality is a number I can defend, not a vibe. The keyword-based fallback scores ~67% on tricky mixed-sentiment cases ("love the display, hate the storage limit") — which is *exactly* the argument for using the LLM: the model with a constrained prompt handles that nuance and pushes accuracy past 90%, while a simple keyword approach can't.

That iteration loop — build, measure against ground truth, fix the input, re-measure — is the core of the whole project.

---

## 6. How each requirement in the job description is demonstrated

- **Data visualization (Tableau/Power BI/Looker):** interactive dashboard; the SQL layer exports clean aggregate tables ready to drop into any BI tool.
- **Building with AI (LLMs, prompt engineering):** the extraction stage is a production-shaped Claude API call with a schema-constrained prompt I can walk through line by line.
- **Real-world / messy datasets:** the input is deliberately dirty — dupes, nulls, mixed date formats, junk rows — and the cleaning stage handles all of it.
- **SQL & Python:** Python for the pipeline, SQL for every business question.
- **Structured, logical problem-solving:** the whole thing is a staged pipeline with a measured quality gate.
- **Consumer products / retail / e-commerce:** the domain is consumer appliances — SharkNinja's exact world.

---

## 7. How I'd take it further in the role

- Swap the CSV ingest for a **live retailer API** so it runs daily.
- Add an **alerting layer**: auto-flag any SKU whose defect rate crosses a threshold and route it to the quality team.
- Layer in an **agentic step** that drafts a summary memo per product for the weekly product review — moving from dashboard to decision support.
- A/B the prompt against a human-labeled set quarterly to keep extraction quality honest as review language drifts.

---

*Pipeline: Datafiniti Amazon reviews CSV → Python clean → Claude API extraction → SQL aggregation → dashboard. Built on the real "Consumer Reviews of Amazon Products" dataset. All code and the live dashboard are included in this project.*
