import csv
import hashlib
import io
import json
import unittest
from pathlib import Path

from src.clean import ANALYTIC_FIELDS, clean_bytes, csv_bytes

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "raw_data.csv"
CLEAN = ROOT / "data" / "processed" / "clean_data.csv"


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = RAW.read_bytes()
        cls.raw = list(csv.DictReader(io.StringIO(cls.raw_bytes.decode("utf-8-sig"))))
        cls.clean = list(csv.DictReader(io.StringIO(CLEAN.read_bytes().decode("utf-8-sig"))))
        cls.quality = json.loads((ROOT / "outputs" / "quality_statistics.json").read_text(encoding="utf-8"))
        cls.collection = json.loads((ROOT / "outputs" / "collection_log.json").read_text(encoding="utf-8"))

    def test_raw_preserved_and_clean_reproducible(self):
        before = hashlib.sha256(self.raw_bytes).hexdigest()
        rows, quality, log = clean_bytes(self.raw_bytes)
        self.assertEqual(csv_bytes(rows), CLEAN.read_bytes())
        self.assertEqual(quality, self.quality)
        self.assertEqual(hashlib.sha256(RAW.read_bytes()).hexdigest(), before)
        self.assertEqual(before, self.collection["raw_sha256"])
        self.assertEqual(log["rules"]["duplicate_removed"], 69)

    def test_counts_completeness_and_no_seller_fields(self):
        self.assertEqual(len(self.raw), 480)
        self.assertEqual(len(self.clean), 411)
        self.assertGreaterEqual(self.quality["analytic_field_completeness"], 0.9)
        observed = sum(bool(row[field]) for row in self.clean for field in ANALYTIC_FIELDS)
        self.assertAlmostEqual(observed / (len(self.clean) * len(ANALYTIC_FIELDS)),
                               self.quality["analytic_field_completeness"], places=4)
        self.assertFalse(any("seller" in field for field in self.raw[0]))
        self.assertFalse(any("seller" in field for field in self.clean[0]))
        self.assertEqual(len({row["listing_id"] for row in self.clean}), 411)

    def test_fifty_row_sample_matches_raw_prefix(self):
        with (ROOT / "data" / "sample" / "first_50.csv").open(encoding="utf-8-sig", newline="") as handle:
            sample = list(csv.DictReader(handle))
        self.assertEqual(len(sample), 50)
        self.assertEqual(sample, self.raw[:50])

    def test_manual_spot_check(self):
        by_id = {row["listing_id"]: row for row in self.clean}
        shokz = by_id["157620004131"]
        self.assertEqual(shokz["brand"], "Shokz")
        self.assertEqual(shokz["price_usd"], "149.99")
        self.assertEqual(shokz["rating"], "5.0")
        self.assertEqual(shokz["reviews_count"], "1")
        self.assertEqual(shokz["scrape_date"], "2026-01-17")
        apple = by_id["389238481744"]
        self.assertEqual(apple["price_usd"], "169.99")
        self.assertEqual(apple["watchers_count"], "109")

    def test_missing_field_explained(self):
        from src.clean import CleanError
        with self.assertRaisesRegex(CleanError, "缺少必需字段"):
            clean_bytes(b"listing_id,title\n1,test\n")


if __name__ == "__main__":
    unittest.main()

