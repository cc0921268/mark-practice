"""Inspect only local public-source review text for manual sample selection."""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data" / "raw" / "beats_reviews_source.csv").open(encoding="utf-8-sig", newline="")))
patterns = {
    "price": r"expensive|overpriced|not worth|pricey|waste of money|price",
    "delivery": r"delivery|shipping|arrived late|arrive on time|ship",
    "packaging": r"packag|box|sealed",
    "battery": r"battery|charging|charge",
}
for category, pattern in patterns.items():
    print("\nCATEGORY", category)
    eligible = [row for row in rows if row["content"].strip() and len(row["content"]) <= 800 and re.search(pattern, row["content"], re.I)]
    print("eligible", len(eligible))
    for row in eligible[:18]:
        match = re.search(pattern, row["content"], re.I)
        excerpt = row["content"][max(0, match.start() - 75):min(len(row["content"]), match.end() + 95)].replace("\n", " ")
        print(row["review_id"], row["product_name"], "len=" + str(len(row["content"])), repr(excerpt))

