"""
03_sql_analysis.py
Loads enriched reviews into SQLite and answers the BUSINESS QUESTIONS
with SQL. Exports aggregated tables for the dashboard.
"""
import pandas as pd, sqlite3, json

import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(_ROOT, "data", "reviews.db")
ENR = os.path.join(_ROOT, "data", "enriched_reviews.csv")

df = pd.read_csv(ENR)
con = sqlite3.connect(DB)
df.to_sql("reviews", con, if_exists="replace", index=False)

# explode themes into a long table for theme-level analysis
rows = []
for _, r in df.iterrows():
    if isinstance(r["themes"], str) and r["themes"]:
        for th in r["themes"].split("|"):
            rows.append({"review_id": r["review_id"],
                         "product": r["product"], "theme": th,
                         "sentiment": r["sentiment"], "defect_risk": int(r["defect_risk"])})
pd.DataFrame(rows).to_sql("review_themes", con, if_exists="replace", index=False)

Q = {
"product_scorecard": """
  SELECT product,
         COUNT(*) AS reviews,
         ROUND(AVG(rating),2) AS avg_rating,
         ROUND(AVG(sentiment_score),2) AS avg_sentiment,
         SUM(defect_risk) AS defect_flags,
         ROUND(100.0*SUM(defect_risk)/COUNT(*),1) AS defect_rate_pct,
         SUM(return_signal) AS return_signals
  FROM reviews GROUP BY product ORDER BY defect_rate_pct DESC""",

"top_complaints": """
  SELECT theme, COUNT(*) AS mentions
  FROM review_themes WHERE sentiment='negative'
  GROUP BY theme ORDER BY mentions DESC LIMIT 6""",

"defect_by_theme": """
  SELECT theme, COUNT(*) AS defect_mentions
  FROM review_themes WHERE defect_risk=1
  GROUP BY theme ORDER BY defect_mentions DESC LIMIT 6""",

"monthly_trend": """
  SELECT strftime('%Y-%m', review_date) AS month,
         COUNT(*) AS reviews,
         ROUND(AVG(sentiment_score),2) AS avg_sentiment,
         ROUND(100.0*SUM(defect_risk)/COUNT(*),1) AS defect_rate_pct
  FROM reviews GROUP BY month ORDER BY month""",

"sentiment_split": """
  SELECT sentiment, COUNT(*) AS n FROM reviews GROUP BY sentiment""",
}

results = {}
for name, sql in Q.items():
    res = pd.read_sql(sql, con)
    results[name] = res
    print(f"\n=== {name} ===")
    print(res.to_string(index=False))

# dump to JSON for the dashboard
with open(os.path.join(_ROOT, "output", "dashboard_data.json"), "w") as f:
    json.dump({k: v.to_dict("records") for k, v in results.items()}, f, indent=2, default=str)
con.close()
print("\nExported dashboard_data.json")
