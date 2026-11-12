import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

from src.competitive_intelligence import (
    DataError, PRODUCTS, REVIEWS, WEIGHTS, SCENARIOS, calculate, load_inputs, sensitivity,
)

ROOT = Path(__file__).resolve().parents[1]


class CompetitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.products, cls.reviews = load_inputs()

    def test_weights_and_manual_score(self):
        self.assertAlmostEqual(sum(WEIGHTS.values()), 1.0)
        self.assertTrue(all(abs(sum(weights.values()) - 1.0) < 1e-9 for weights in SCENARIOS.values()))
        scores = calculate(self.products, self.reviews)["scores"].set_index("competitor")
        row = scores.loc["Sennheiser"]
        manual = (row["consumer_overlap"] * .30 + row["product_overlap"] * .25
                  + row["price_overlap"] * .20 + row["brand_heat"] * .25)
        self.assertAlmostEqual(manual, row["threat_index"], places=3)
        self.assertEqual(int(row["rank"]), 1)
        self.assertEqual(int(scores.loc["Jabra", "rank"]), 2)

    def test_sparse_review_brand_unranked_and_product_warning(self):
        scores = calculate(self.products, self.reviews)["scores"].set_index("competitor")
        self.assertEqual(scores.loc["Apple", "rank_status"], "insufficient_review_sample")
        self.assertTrue(pd.isna(scores.loc["Apple", "threat_index"]))
        self.assertTrue(bool(scores.loc["Jabra", "product_sample_warning"]))
        self.assertEqual(int(scores.loc["Jabra", "product_listing_count"]), 1)

    def test_sensitivity_explains_rank_reversal(self):
        frame = sensitivity(self.products, self.reviews, "Skullcandy")
        base = frame.loc[frame["scenario"].eq("base")].set_index("competitor")
        stress = frame.loc[frame["scenario"].eq("consumer_dominant_stress")].set_index("competitor")
        self.assertEqual(int(base.loc["Sennheiser", "rank"]), 1)
        self.assertEqual(int(stress.loc["Jabra", "rank"]), 1)

    def test_evidence_and_original_hashes(self):
        before_products = hashlib.sha256(PRODUCTS.read_bytes()).hexdigest()
        before_reviews = hashlib.sha256(REVIEWS.read_bytes()).hexdigest()
        result = calculate(self.products, self.reviews)
        self.assertEqual(len(result["evidence"]), 5 * 4)
        self.assertTrue(result["evidence"]["source_fields"].str.len().gt(0).all())
        self.assertEqual(hashlib.sha256(PRODUCTS.read_bytes()).hexdigest(), before_products)
        self.assertEqual(hashlib.sha256(REVIEWS.read_bytes()).hexdigest(), before_reviews)
        self.assertEqual(before_products, "0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55")

    def test_bad_weights_and_fabricated_quote_rejected(self):
        with self.assertRaisesRegex(DataError, "合计为 100%"):
            calculate(self.products, self.reviews, weights={**WEIGHTS, "brand_heat": .20})
        review_file = ROOT / "data" / "processed" / "encoded_reviews.json"
        data = json.loads(review_file.read_text(encoding="utf-8"))
        record = next(row for row in data["records"] if row["pain_tags"])
        key = record["pain_tags"][0]
        record["evidence"]["pain_tags"][key] = "a fabricated quotation"
        bad = ROOT / "outputs" / "test_bad_reviews.json"
        try:
            bad.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(DataError, "不是对应原文子串"):
                load_inputs(PRODUCTS, bad)
        finally:
            bad.unlink(missing_ok=True)

    def test_ninth_week_mini_sample_ranking(self):
        sample = ROOT / "data" / "sample"
        products, reviews = load_inputs(sample / "mini_products.csv", sample / "mini_encoded_reviews.json")
        rows = calculate(products, reviews, "Focus")["scores"].set_index("competitor")
        self.assertEqual(int(rows.loc["Alpha", "rank"]), 1)
        self.assertEqual(int(rows.loc["Beta", "rank"]), 2)
        self.assertEqual(float(rows.loc["Alpha", "consumer_overlap"]), 100.0)
        self.assertEqual(float(rows.loc["Alpha", "product_overlap"]), 100.0)
        self.assertEqual(float(rows.loc["Alpha", "price_overlap"]), 100.0)
        self.assertEqual(float(rows.loc["Beta", "consumer_overlap"]), 0.0)


if __name__ == "__main__":
    unittest.main()

