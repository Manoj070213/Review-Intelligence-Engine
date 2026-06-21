"""
01_generate_data.py
Simulates a realistic, MESSY consumer-product review dataset.
Stands in for an Amazon/retailer review export. Intentionally dirty:
typos, mixed-language, nulls, dupes, inconsistent dates, junk rows.
"""
import pandas as pd, random, datetime as dt
from faker import Faker

fake = Faker()
random.seed(42); Faker.seed(42)

PRODUCTS = {
    "SN-VAC-100": "Ninja Cordless Vacuum",
    "SN-BLD-200": "Ninja Pro Blender",
    "SN-FRY-300": "Ninja Air Fryer XL",
    "SN-VAC-150": "Shark Robot Vacuum",
    "SN-GRL-400": "Ninja Indoor Grill",
}

# Real-world complaint/praise seeds per theme (messy phrasing on purpose)
POS = [
    "works great love it", "best purchase this year!!", "powerful suction wow",
    "super easy to clean", "quiet and fast", "cooks evenly every time",
    "battery lasts forever", "saved me so much time", "great value for money",
    "my kitchen game changer", "crispy results amazing", "sleek design fits counter",
]
NEG = [
    "stopped working after 2 weeks", "battery dies so fast :(", "way too loud",
    "leaked all over counter", "broke on day 3, returning it",
    "customer service was useless", "doesnt fit under furniture",
    "smells like burning plastic", "way overpriced for what it is",
    "app keeps disconnecting", "scratches the floor", "lid cracked first use",
]
MIXED = [
    "good suction but battery weak", "love the design hate the noise",
    "works ok but app is buggy", "cooks well, cleanup is a pain",
    "fast but feels cheaply made", "great when it works, breaks often",
]
JUNK = ["asdfgh", ".", "5 stars", "👍👍👍", "test review ignore", ""]

rows = []
start = dt.date(2024, 1, 1)
for i in range(1200):
    sku = random.choice(list(PRODUCTS))
    r = random.random()
    if r < 0.42:
        text, star = random.choice(POS), random.choice([4,5,5,5])
    elif r < 0.78:
        text, star = random.choice(NEG), random.choice([1,1,2,3])
    elif r < 0.93:
        text, star = random.choice(MIXED), random.choice([2,3,3,4])
    else:
        text, star = random.choice(JUNK), random.choice([1,3,5])

    # inject messiness
    if random.random() < 0.15: text = text.upper()
    if random.random() < 0.10: text = text + " " + random.choice(POS+NEG)
    if random.random() < 0.08: star = None              # missing rating
    if random.random() < 0.05: text = None              # missing text

    d = start + dt.timedelta(days=random.randint(0, 540))
    # inconsistent date formats
    date_str = random.choice([d.isoformat(), d.strftime("%m/%d/%Y"), d.strftime("%d-%b-%y")])

    rows.append({
        "review_id": f"R{100000+i}",
        "sku": sku,
        "product": PRODUCTS[sku],
        "rating": star,
        "review_text": text,
        "review_date": date_str,
        "verified": random.choice([True, True, False, None]),
        "helpful_votes": random.choice([0,0,1,2,5,None]),
    })

df = pd.DataFrame(rows)
# add ~40 duplicate rows (real exports have these)
df = pd.concat([df, df.sample(40, random_state=1)], ignore_index=True)
df.to_csv("/home/claude/review_intel/data/raw_reviews.csv", index=False)
print(f"Wrote {len(df)} raw rows ({df.review_text.isna().sum()} null text, "
      f"{df.rating.isna().sum()} null rating, 40 dupes injected)")
