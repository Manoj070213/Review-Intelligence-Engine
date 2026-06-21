"""
02_clean_and_extract.py
Step 1: Clean the messy export (the 'Details Make the Difference' part).
Step 2: Run each review through an LLM to extract STRUCTURED insight
        (sentiment, themes, defect_risk, feature_request).

The LLM call uses the real Anthropic API when ANTHROPIC_API_KEY is set.
If not, a transparent rule-based simulator stands in so the full pipeline
runs end-to-end. The exact production prompt is in build_prompt().
"""
import pandas as pd, json, os, re, datetime as dt

import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(_ROOT, "data", "raw_reviews.csv")
OUT = os.path.join(_ROOT, "data", "enriched_reviews.csv")

THEMES = ["battery_life", "screen_display", "performance_speed", "durability",
          "ease_of_use", "price_value", "connectivity_wifi", "kids_usability",
          "storage_capacity", "customer_service"]

# ---------- STEP 1: CLEAN ----------
def parse_date(s):
    if pd.isna(s): return pd.NaT
    s = str(s)
    # real Datafiniti dates look like 2017-03-02T00:00:00.000Z
    try:
        return pd.to_datetime(s, errors="raise").date()
    except Exception:
        pass
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%y"):
        try: return dt.datetime.strptime(s, fmt).date()
        except ValueError: continue
    return pd.NaT

def clean(df):
    before = len(df)
    df = df.drop_duplicates(subset="review_id")              # kill dupes
    df = df.dropna(subset=["review_text"])                   # need text to analyze
    df["review_text"] = df["review_text"].str.strip()
    df = df[df["review_text"].str.len() >= 4]                # drop junk like "." "👍"
    df = df[~df["review_text"].str.fullmatch(r"[^a-zA-Z]+", na=False)]  # drop non-text
    df["review_date"] = df["review_date"].apply(parse_date)
    df = df.dropna(subset=["review_date"])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    if "verified" in df.columns:
        df["verified"] = df["verified"].fillna(False)
    print(f"  Cleaning: {before} -> {len(df)} rows "
          f"({before-len(df)} removed: dupes/nulls/junk)")
    return df.reset_index(drop=True)

# ---------- STEP 2: AI EXTRACTION ----------
def build_prompt(text, product):
    return f"""You are a product-insights analyst for a consumer appliance company.
Analyze this customer review and return ONLY a JSON object, no other text.

Product: {product}
Review: "{text}"

Return this exact schema:
{{
  "sentiment": "positive" | "negative" | "mixed",
  "sentiment_score": <float -1.0 to 1.0>,
  "themes": [<subset of {THEMES}>],
  "defect_risk": <true if review signals a malfunction, breakage, or safety issue>,
  "return_signal": <true if customer mentions returning/refunding>,
  "feature_request": <string or null>
}}"""

def call_real_api(text, product):
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=400,
        messages=[{"role": "user", "content": build_prompt(text, product)}],
    )
    raw = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)

def simulate(text, product):
    """Transparent fallback so pipeline runs without a key. Mirrors LLM output shape."""
    t = text.lower()
    kw = {
        "battery_life": ["battery","charge","charging","dies","lasts","power"],
        "screen_display": ["screen","display","resolution","bright","hd","picture"],
        "performance_speed": ["fast","slow","lag","freeze","quick","responsive","speed"],
        "durability": ["broke","crack","stopped","cheap","durable","died","quit","defective"],
        "ease_of_use": ["easy","simple","intuitive","setup","user friendly","easy to use"],
        "price_value": ["price","overpriced","value","money","cheap","worth","affordable","deal"],
        "connectivity_wifi": ["wifi","wi-fi","connect","disconnect","bluetooth","network"],
        "kids_usability": ["kid","kids","child","children","grandkid","daughter","son"],
        "storage_capacity": ["storage","memory","gb","space","sd card"],
        "customer_service": ["customer service","support","return","refund","warranty","replace"],
    }
    themes = [th for th, words in kw.items() if any(w in t for w in words)]
    neg_w = ["broke","stopped","dies","died","crack","overpriced","useless","defective",
             "slow","lag","freeze","disappointed","return","refund","junk","waste","poor","quit"]
    pos_w = ["great","love","best","easy","fast","perfect","excellent","amazing","value",
             "happy","recommend","awesome","works well","worth","fantastic","good"]
    n = sum(w in t for w in neg_w); p = sum(w in t for w in pos_w)
    if p and n: sent, score = "mixed", round((p-n)/(p+n)*0.5, 2)
    elif n: sent, score = "negative", round(-min(0.4+0.2*n, 1.0), 2)
    elif p: sent, score = "positive", round(min(0.4+0.2*p, 1.0), 2)
    else: sent, score = "mixed", 0.0
    defect = any(w in t for w in ["broke","stopped","crack","died","defective","quit","won't turn on","wont turn on"])
    ret = any(w in t for w in ["return","refund","sent it back","sending it back"])
    fr = ("longer battery life" if ("battery" in t and n) else
          "more storage" if ("storage" in t and n) else
          "faster performance" if any(w in t for w in ["slow","lag","freeze"]) else None)
    return {"sentiment": sent, "sentiment_score": score, "themes": themes,
            "defect_risk": defect, "return_signal": ret, "feature_request": fr}

def extract(df):
    use_api = bool(os.getenv("ANTHROPIC_API_KEY"))
    print(f"  Extraction engine: {'REAL Anthropic API' if use_api else 'rule-based simulator (no API key set)'}")
    recs = []
    for _, r in df.iterrows():
        fn = call_real_api if use_api else simulate
        try: out = fn(r.review_text, r.product)
        except Exception as e: out = simulate(r.review_text, r.product)
        recs.append(out)
    ext = pd.json_normalize(recs)
    ext["themes"] = ext["themes"].apply(lambda x: "|".join(x) if x else "")
    return pd.concat([df.reset_index(drop=True), ext], axis=1)

if __name__ == "__main__":
    print("STEP 1 — CLEAN")
    df = clean(pd.read_csv(RAW))
    print("STEP 2 — AI EXTRACTION")
    enriched = extract(df)
    enriched.to_csv(OUT, index=False)
    print(f"  Wrote {len(enriched)} enriched rows -> {OUT}")
    print(f"  Defect-risk flagged: {enriched.defect_risk.sum()} | "
          f"Return signals: {enriched.return_signal.sum()}")
