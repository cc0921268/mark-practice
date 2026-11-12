import hashlib
import unittest
from pathlib import Path

from src.analysis import DataError, analyse_csv

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "sample"


class AnalysisTests(unittest.TestCase):
    def test_normal_means_match_manual_check(self):
        result = analyse_csv((SAMPLES / "normal.csv").read_bytes())
        self.assertEqual(result["valid_rows"], 4)
        self.assertEqual(result["skipped_rows"], 0)
        brands = {item["brand"]: item for item in result["brands"]}
        self.assertEqual(brands["星河"]["average_price"], 150.0)
        self.assertEqual(brands["星河"]["average_rating"], 4.5)
        self.assertEqual(brands["青竹"]["average_price"], 100.0)
        self.assertEqual(brands["青竹"]["average_rating"], 4.0)

    def test_missing_field_explains_which_field(self):
        with self.assertRaisesRegex(DataError, "缺少必需字段：rating"):
            analyse_csv((SAMPLES / "missing_field.csv").read_bytes())

    def test_empty_values_are_skipped_without_modifying_source(self):
        source = SAMPLES / "empty_values.csv"
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        result = analyse_csv(source.read_bytes())
        self.assertEqual(result["valid_rows"], 2)
        self.assertEqual(result["skipped_rows"], 3)
        self.assertEqual(len(result["warnings"]), 3)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_all_invalid_rows_produce_clear_error(self):
        with self.assertRaisesRegex(DataError, "没有可分析的数据"):
            analyse_csv(b"brand,price,rating\n,10,4\n")


if __name__ == "__main__":
    unittest.main()
