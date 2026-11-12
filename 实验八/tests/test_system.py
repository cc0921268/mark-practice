import copy
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src import system
from src import competitive_intelligence, content_opportunity, consumer_insight_engine, marketing_workflow
from src.api_client import ApiError, call_model
from src.path_security import project_path
from src.path_security import project_source


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.products = system.load_products()
        cls.encoded, cls.reviews = system.load_encoded()

    def test_integrated_pipeline_and_evidence(self):
        result = system.analyze(self.products, self.encoded, "Skullcandy")
        self.assertAlmostEqual(sum(result["competition"]["summary"]["weights"].values()), 1.0)
        self.assertEqual(result["insight"]["summary"]["review_sample_size"], len(self.encoded))
        self.assertGreaterEqual(len(result["content"]["briefs"]), 5)
        for row in self.encoded:
            for quote in row["evidence"]["pain_tags"].values():
                self.assertIn(quote, row["review_text"])

    def test_missing_columns_and_original_unchanged(self):
        before = project_path(system.PRODUCTS).read_bytes()
        with self.assertRaisesRegex(ValueError, "price_usd"):
            system.load_products(io.BytesIO(pd.DataFrame({"brand": ["X"]}).to_csv(index=False).encode()))
        self.assertEqual(before, project_path(system.PRODUCTS).read_bytes())

    def test_unfamiliar_brand_names(self):
        products = self.products.copy()
        mapping = {brand: f"Novel{index}" for index, brand in enumerate(sorted(products.brand.unique()))}
        products["brand"] = products.brand.map(mapping)
        coded = copy.deepcopy(self.encoded)
        for row in coded:
            row["brand"] = mapping.get(row["brand"], row["brand"])
        result = system.analyze(products, coded, mapping["Skullcandy"])
        self.assertGreater(len(result["competition"]["scores"]), 0)

    def test_unfamiliar_reviews_remain_unclassified(self):
        coded = copy.deepcopy(self.encoded)
        for row in coded:
            row["pain_tags"] = []
            row["evidence"]["pain_tags"] = {}
        result = system.analyze(self.products, coded, "Skullcandy")
        self.assertEqual(result["competition"]["summary"]["ranked_competitors"], 0)
        self.assertEqual(result["content"]["briefs"], [])

    def test_ab_denominator_and_db(self):
        data = pd.DataFrame([
            {"respondent_id": "x", "variant": "A", "click_intent": 4, "purchase_intent": 3, "feedback": "a"},
            {"respondent_id": "y", "variant": "B", "click_intent": 5, "purchase_intent": 4, "feedback": "b"}])
        table, meta = system.analyze_ab(data)
        self.assertEqual(meta["sample_size"], 2)
        self.assertTrue((table.sample_size == 1).all())
        with tempfile.TemporaryDirectory(dir=system.ROOT / "tests") as tmp:
            db = Path(tmp) / "test.sqlite3"
            system.save_profile("X", "audience", "description", db)
            system.save_run("X", "analysis", "completed", {"n": 2}, path=db)
            self.assertEqual(len(system.history(db)), 1)

    def test_all_path_entry_points_reject_outside(self):
        outside = system.ROOT.parent / "__outside_project__" / "input.csv"
        actions = [
            lambda: project_path(outside),
            lambda: system.load_products(outside),
            lambda: system.load_encoded(outside),
            lambda: system.history(outside),
            lambda: consumer_insight_engine.load_reviews(outside),
            lambda: consumer_insight_engine.run(outside, system.ANNOTATIONS, system.PRODUCTS,
                                                system.ROOT / "outputs"),
            lambda: competitive_intelligence.load_inputs(outside, system.ROOT / "data/processed/encoded_reviews.json"),
            lambda: content_opportunity.load_inputs(outside, system.PRODUCTS,
                                                     system.ROOT / "data/processed/selling_points.csv",
                                                     system.ROOT / "data/processed/scores.csv"),
            lambda: marketing_workflow.run_workflow(output_root=outside),
        ]
        for action in actions:
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, "项目外文件"):
                action()
        with self.assertRaisesRegex(ValueError, "项目外文件"):
            project_path(Path("..") / "__outside_project__" / "input.csv")
        with self.assertRaisesRegex(ValueError, "内存上传数据"):
            project_source(type("FakeFile", (), {"read": lambda self: b"data"})())
        self.assertIsInstance(project_source(io.BytesIO(b"data")), io.BytesIO)
        with self.assertRaisesRegex(ApiError, "file://"):
            call_model(outside.as_uri(), {})


if __name__ == "__main__":
    unittest.main()

