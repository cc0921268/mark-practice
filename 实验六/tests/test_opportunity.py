import copy
import hashlib
import json
import unittest
from pathlib import Path

from src.brand_voice import validate_brief, validate_text
from src.content_opportunity import (
    DataError, ENCODED, PRODUCTS, SELLING, SCORES, calculate, load_inputs,
)

ROOT = Path(__file__).resolve().parents[1]


class OpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_inputs()
        cls.result = calculate(*cls.inputs)

    def test_formula_and_six_briefs(self):
        matrix = self.result["theme_matrix"].set_index("theme")
        self.assertEqual(float(matrix.loc["device_failure", "opportunity_score"]), 30.0)
        self.assertEqual(int(matrix.loc["device_failure", "user_mentions"]), 9)
        self.assertEqual(int(matrix.loc["device_failure", "competitor_titles_covered"]), 0)
        self.assertEqual(int(matrix.loc["battery", "user_mentions"]), 8)
        self.assertEqual(int(matrix.loc["battery", "competitor_titles_covered"]), 1)
        self.assertAlmostEqual(float(matrix.loc["battery", "opportunity_score"]),
                               round((8 / 30 * 100) * (1 - 1 / 13), 2), places=2)
        self.assertEqual(len(self.result["briefs"]), 6)

    def test_pseudo_gap_and_covered_theme(self):
        matrix = self.result["theme_matrix"].set_index("theme")
        self.assertEqual(matrix.loc["taste", "status"], "pseudo_gap_low_user_interest")
        self.assertEqual(float(matrix.loc["taste", "opportunity_score"]), 0.0)
        self.assertEqual(matrix.loc["connectivity", "status"], "covered_or_low_gap")
        self.assertEqual(int(matrix.loc["connectivity", "competitor_titles_covered"]), 13)

    def test_evidence_and_voice_are_enforced(self):
        reviews = {row["review_id"]: row for row in self.inputs[0]}
        for row in self.result["evidence_record"].to_dict("records"):
            if row["evidence_type"] == "user_review":
                self.assertIn(row["exact_quote_or_title"], reviews[row["source_id"]]["review_text"])
        for brief in self.result["briefs"]:
            self.assertEqual(validate_brief(brief), [])
            self.assertGreaterEqual(len(set(brief["user_evidence_ids"])), 3)
            self.assertEqual(len(brief["competitor_checked_listing_ids"]), 13)
        self.assertEqual(validate_text("在统一音量条件下实测续航，并说明充电排查步骤。"), [])
        self.assertTrue(validate_text("我们的耳机永久零故障，行业第一。"))

    def test_source_hashes_and_exclusion(self):
        self.assertEqual(hashlib.sha256(PRODUCTS.read_bytes()).hexdigest(),
                         "0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55")
        self.assertEqual(hashlib.sha256(ENCODED.read_bytes()).hexdigest(),
                         "8d53e144acbc29de7e19e4cff3bf7f4817b5c6f6a4f769c0d385a2502a737937")
        self.assertEqual(len(self.result["excluded_accessories"]), 1)
        self.assertEqual(self.result["summary"]["competitor_title_sample_size"], 13)
        self.assertEqual(self.result["summary"]["selling_points_anc_count_verified"], 2)

    def test_invalid_review_quote_rejected(self):
        source = json.loads(ENCODED.read_text(encoding="utf-8"))
        data = copy.deepcopy(source)
        record = next(row for row in data["records"] if row["pain_tags"])
        tag = record["pain_tags"][0]
        record["evidence"]["pain_tags"][tag] = "invented quote"
        temporary = ROOT / "outputs" / "invalid_test_input.json"
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(DataError, "不是同条原文子串"):
                load_inputs(temporary, PRODUCTS, SELLING, SCORES)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()


