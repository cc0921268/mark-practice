import copy
import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

from src.consumer_insight_engine import InputError, encode, load_reviews, statistics, run

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "data" / "raw" / "reviews.csv"
ANNOTATIONS = ROOT / "data" / "processed" / "semantic_annotations.json"
PRODUCTS = ROOT / "data" / "processed" / "clean_data.csv"


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviews = load_reviews(REVIEWS)
        cls.annotations = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
        cls.products = pd.read_csv(PRODUCTS, dtype=str, keep_default_na=False, encoding="utf-8-sig")

    def test_main_results_recalculate_and_raw_is_unchanged(self):
        raw_hash = hashlib.sha256(REVIEWS.read_bytes()).hexdigest()
        records = encode(self.reviews, self.annotations)
        stats = statistics(records, self.products)
        stored = pd.read_csv(ROOT / "outputs" / "pain_ranking.csv", encoding="utf-8-sig")
        pd.testing.assert_frame_equal(stats["pain_ranking"], stored, check_dtype=False)
        self.assertEqual(stats["summary"]["review_sample_size"], 30)
        self.assertEqual(hashlib.sha256(REVIEWS.read_bytes()).hexdigest(), raw_hash)
        self.assertEqual(hashlib.sha256(PRODUCTS.read_bytes()).hexdigest(),
                         "0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55")

    def test_percent_denominator_and_zero_categories(self):
        records = encode(self.reviews, self.annotations)
        stats = statistics(records, self.products)
        pain = stats["pain_ranking"].set_index("pain_tag")
        self.assertEqual(int(pain.loc["device_failure", "count"]), 9)
        self.assertEqual(int(pain.loc["device_failure", "denominator"]), 30)
        self.assertEqual(float(pain.loc["device_failure", "percent"]), 30.0)
        self.assertEqual(int(pain.loc["taste", "count"]), 0)
        self.assertEqual(int(pain.loc["delivery", "count"]), 0)
        self.assertTrue((pain["denominator"] == pain["sample_size"]).all())

    def test_three_input_examples(self):
        normal = load_reviews(ROOT / "data" / "sample" / "case_normal.csv")
        good = json.loads((ROOT / "data" / "sample" / "case_normal_codes.json").read_text(encoding="utf-8"))
        bad = json.loads((ROOT / "data" / "sample" / "case_fabricated_quote.json").read_text(encoding="utf-8"))
        records = encode(normal, good)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["pain_tags"], ["price", "battery"])
        with self.assertRaisesRegex(InputError, "缺少字段"):
            load_reviews(ROOT / "data" / "sample" / "case_missing_field.csv")
        with self.assertRaisesRegex(InputError, "证据不是原评论子串"):
            encode(normal, bad)

    def test_missing_or_duplicate_codes_rejected(self):
        with self.assertRaisesRegex(InputError, "不完全一致"):
            encode(self.reviews, self.annotations[:-1])
        duplicate = copy.deepcopy(self.annotations)
        duplicate[1]["review_id"] = duplicate[0]["review_id"]
        with self.assertRaisesRegex(InputError, "重复"):
            encode(self.reviews, duplicate)

    def test_encoded_evidence_and_source_ids(self):
        records = encode(self.reviews, self.annotations)
        self.assertEqual({record["review_id"] for record in records}, set(self.reviews["review_id"]))
        for record in records:
            text = record["review_text"]
            for value in record["evidence"].values():
                if isinstance(value, list):
                    self.assertTrue(all(quote in text for quote in value))
                elif isinstance(value, dict):
                    self.assertTrue(all(quote in text for quote in value.values()))
                elif isinstance(value, str):
                    self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()

