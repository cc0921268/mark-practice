"""Persist four reproducible fault injections and their resulting run logs."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.marketing_workflow import WorkflowError, run_workflow

ROOT = Path(__file__).resolve().parents[1]
cases = [
    ("api_503_once", {"target_consumer": "http_503_once"}, "completed_after_retry"),
    ("api_unavailable", {"target_consumer": "http_503"}, "completed_with_fallback"),
    ("invalid_json", {"target_consumer": "invalid_json"}, "failed_readably"),
    ("missing_field", {"target_consumer": "missing_field"}, "failed_readably"),
    ("timeout", {"target_consumer": "timeout"}, "completed_with_fallback"),
]
results = []
for name, inject, expected in cases:
    try:
        value = run_workflow(output_root=ROOT / "outputs" / "debug_runs", inject=inject,
                             timeout=.04 if name == "timeout" else .5, retries=1)
        run_dir = Path(value["run_dir"])
        record = json.loads((run_dir / "06_target_consumer.json").read_text(encoding="utf-8"))
        actual = "completed_with_fallback" if record["output"]["origin"] == "deterministic_local_fallback" else "completed_after_retry"
        message = record["output"]["origin"]
    except WorkflowError as exc:
        actual = "failed_readably"
        message = str(exc)
        run_dir = sorted((ROOT / "outputs" / "debug_runs").iterdir(), reverse=True)[0]
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected}, got {actual}")
    results.append({"case": name, "expected": expected, "actual": actual,
                    "run_dir": str(run_dir.relative_to(ROOT)), "message": message})
(ROOT / "outputs" / "debug_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print("Debug scenarios: 503 retry, API fallback, invalid JSON, missing field, timeout fallback OK")

