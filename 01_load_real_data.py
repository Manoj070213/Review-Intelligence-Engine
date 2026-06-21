"""
01_load_real_data.py  (REAL DATA version)
Loads the Datafiniti 'Consumer Reviews of Amazon Products' dataset and maps it
into the schema the rest of the pipeline expects. Replaces the synthetic
generator. Keeps the data intentionally close to raw so the cleaning step in
02 still has real work to do (it does: mixed nulls, ISO timestamps, skew).

Source columns used:
  name -> product        reviews.rating -> rating
  reviews.text -> review_text   reviews.date -> review_date
  reviews.doRecommend, reviews.numHelpful -> kept as signals
"""
import pandas as pd, os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(_ROOT, "data", "amazon_reviews_real.csv")
OUT = os.path.join(_ROOT, "data", "raw_reviews.csv")

# Cap the run so the demo (and any API extraction) stays fast/cheap.
# Bump or remove SAMPLE_N to run the full 28k.
SAMPLE_N = 1500

df = pd.read_csv(SRC, low_memory=False)
print(f"Loaded {len(df):,} real Amazon reviews across {df['name'].nunique()} products")

# build a short SKU from the product name so the dashboard reads cleanly
def short_name(n):
    n = str(n)
    if "AAA" in n: return "AmazonBasics AAA Batteries"
    if "AA Performance" in n: return "AmazonBasics AA Batteries"
    if "Fire HD 8" in n: return "Fire HD 8 Tablet"
    if "Kids Edition" in n: return "Fire Kids Edition Tablet"
    if "Fire Tablet" in n: return "Fire 7 Tablet"
    if "Echo" in n: return "Amazon Echo"
    if "Tap" in n: return "Amazon Tap"
    if "Kindle" in n: return "Kindle E-reader"
    return n[:40]

out = pd.DataFrame({
    "review_id": df["reviews.id"].fillna(pd.Series(range(len(df)))).astype(str)
                  if "reviews.id" in df else range(len(df)),
    "product": df["name"].map(short_name),
    "rating": df["reviews.rating"],
    "review_text": df["reviews.text"],
    "review_date": df["reviews.date"],
    "do_recommend": df["reviews.doRecommend"],
    "helpful_votes": df["reviews.numHelpful"],
})
out["review_id"] = ["R" + str(i).zfill(6) for i in range(len(out))]

# focus on the highest-volume products so trend lines are meaningful
top = out["product"].value_counts().head(6).index
out = out[out["product"].isin(top)]

# stratified-ish sample: keep proportional mix but cap size
if SAMPLE_N and len(out) > SAMPLE_N:
    out = out.sample(SAMPLE_N, random_state=42).reset_index(drop=True)

out.to_csv(OUT, index=False)
print(f"Wrote {len(out):,} rows -> {OUT}")
print("Products kept:", ", ".join(top))
print("Rating mix:", out['rating'].value_counts().sort_index().to_dict())
