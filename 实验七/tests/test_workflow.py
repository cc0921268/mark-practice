import json
import tempfile
import unittest
from pathlib import Path

from src.marketing_workflow import DEFAULT_REQUEST, WorkflowError, run_workflow


class WorkflowTests(unittest.TestCase):
    def test_full_chain_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(DEFAULT_REQUEST, output_root=Path(directory))
            self.assertEqual(result["steps_completed"], 9)
            self.assertEqual(result["status"], "draft_pending_human_review")
            run = Path(result["run_dir"])
            state = json.loads((run / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(len(state["steps"]), 9)
            self.assertTrue(all(item["status"] == "completed" for item in state["steps"].values()))
            self.assertEqual(result["campaign"]["approval_status"], "pending_human_review")
            self.assertGreaterEqual(len(result["campaign"]["evidence_ids"]), 3)
            self.assertTrue((run / "consumer_outputs" / "pain_ranking.csv").exists())
            self.assertTrue((run / "competition_outputs" / "scores.csv").exists())
            self.assertTrue((run / "content_outputs" / "strategy_briefs.json").exists())
            self.assertIn("human_review", (run / "events.jsonl").read_text(encoding="utf-8"))

    def test_transient_http_failure_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(output_root=Path(directory), inject={"target_consumer": "http_503_once"})
            record = json.loads((Path(result["run_dir"]) / "06_target_consumer.json").read_text(encoding="utf-8"))
            self.assertEqual(record["output"]["origin"], "local_http_mock")
            self.assertEqual(len(record["output"]["api_attempts"]), 2)

    def test_api_down_uses_local_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(output_root=Path(directory), inject={"target_consumer": "http_503"}, retries=1)
            record = json.loads((Path(result["run_dir"]) / "06_target_consumer.json").read_text(encoding="utf-8"))
            self.assertEqual(record["output"]["origin"], "deterministic_local_fallback")

    def test_timeout_uses_local_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(output_root=Path(directory), inject={"target_consumer": "timeout"}, timeout=.03, retries=1)
            record = json.loads((Path(result["run_dir"]) / "06_target_consumer.json").read_text(encoding="utf-8"))
            self.assertEqual(record["output"]["origin"], "deterministic_local_fallback")

    def test_invalid_json_and_missing_field_fail_readably(self):
        for fault, phrase in (("invalid_json", "JSON 无法解析"), ("missing_field", "缺少必需字段")):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(WorkflowError, phrase):
                    run_workflow(output_root=Path(directory), inject={"target_consumer": fault})
                run = next(Path(directory).iterdir())
                state = json.loads((run / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(state["status"], "failed")
                self.assertEqual(state["steps"]["target_consumer"]["status"], "failed")


if __name__ == "__main__":
    unittest.main()

