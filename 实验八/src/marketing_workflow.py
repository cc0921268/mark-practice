"""Traceable marketing planning workflow. Run: python -m src.marketing_workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.api_client import ApiError, InvalidResponseError, call_model
from src.mock_model_api import mock_result, start_mock
from src import brand_voice, competitive_intelligence as competition
from src import consumer_insight_engine as consumer
from src import content_opportunity as gap
from src.path_security import project_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = "给蓝牙耳机设计一次新品推广"
STEPS = ("brand_profile", "consumer_insight", "competitive_analysis", "content_gap",
         "brand_voice", "target_consumer", "communication_theme", "channel_plan", "campaign")
MODEL_REQUIRED = {
    "target_consumer": ("segment", "why", "evidence_ids", "status"),
    "communication_theme": ("theme", "message", "source_theme", "evidence_ids", "competitor_listing_ids", "status"),
    "channel_plan": ("channels", "evidence_ids", "status"),
    "campaign": ("name", "objective", "audience", "theme", "channels", "evidence_ids", "competitor_listing_ids", "metric", "claim_boundary", "approval_status"),
}


class WorkflowError(RuntimeError):
    pass


def _write_json(path: Path, value: dict) -> None:
    project_path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _hash(path: Path) -> str:
    return hashlib.sha256(project_path(path).read_bytes()).hexdigest()


def _validate_model(step: str, value: dict, review_ids: set[str], product_ids: set[str]) -> None:
    missing = [field for field in MODEL_REQUIRED[step] if field not in value or value[field] in (None, "", [])]
    if missing:
        raise WorkflowError(f"{step} 的 JSON 缺少必需字段：{', '.join(missing)}")
    if not isinstance(value["evidence_ids"], list) or not set(value["evidence_ids"]).issubset(review_ids):
        raise WorkflowError(f"{step} 的原评论 ID 不存在。")
    if step in ("communication_theme", "campaign"):
        if not isinstance(value["competitor_listing_ids"], list) or not set(value["competitor_listing_ids"]).issubset(product_ids):
            raise WorkflowError(f"{step} 的竞品商品 ID 不存在。")
    if step == "communication_theme" and brand_voice.validate_text(value["message"]):
        raise WorkflowError("传播主题不符合 Brand Voice 规则。")
    if step == "campaign" and value["approval_status"] != "pending_human_review":
        raise WorkflowError("Campaign 必须保持待人工审核状态。")


def run_workflow(request: str = DEFAULT_REQUEST, *, output_root: Path | None = None,
                 inject: dict[str, str] | None = None, api_url: str | None = None,
                 timeout: float = 0.5, retries: int = 2) -> dict:
    if not request.strip():
        raise WorkflowError("请输入营销策划需求。")
    output_root = project_path(output_root or ROOT / "outputs" / "runs")
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = output_root / run_id
    run_dir.mkdir()
    event_file = run_dir / "events.jsonl"
    state = {"version": "v0.7", "run_id": run_id, "request": request,
             "status": "running", "steps": {}, "human_review": "pending"}
    local_server = None
    if api_url is None:
        local_server, api_url = start_mock(inject)
    reviews = None
    products = None
    briefs = None
    review_ids: set[str] = set()
    product_ids: set[str] = set()

    def event(value: dict) -> None:
        with project_path(event_file).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at_utc": datetime.now(timezone.utc).isoformat(), **value}, ensure_ascii=False) + "\n")

    def step(name: str, input_value: dict, action, evidence_sources: list[str]) -> dict:
        position = STEPS.index(name) + 1
        path = run_dir / f"{position:02d}_{name}.json"
        record = {"name": name, "input": input_value, "output": None,
                  "status": "running", "evidence_sources": evidence_sources,
                  "started_at_utc": datetime.now(timezone.utc).isoformat()}
        _write_json(path, record)
        event({"step": name, "status": "running"})
        try:
            value = action()
            record["output"] = value
            record["status"] = "completed"
            state["steps"][name] = {"status": "completed", "file": path.name,
                                     "evidence_sources": evidence_sources}
            return value
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)
            state["steps"][name] = {"status": "failed", "file": path.name, "error": str(exc)}
            raise
        finally:
            record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
            _write_json(path, record)
            event({"step": name, "status": record["status"], "error": record.get("error")})
            _write_json(run_dir / "state.json", state)

    def model_action(name: str, context: dict) -> dict:
        attempts = []
        try:
            result = call_model(api_url, {"step": name, "context": context},
                                timeout=timeout, retries=retries,
                                on_attempt=lambda value: attempts.append(value))
            origin = "local_http_mock" if local_server is not None else "configured_http_api"
            event({"step": name, "api_attempts": attempts, "origin": origin})
        except InvalidResponseError:
            raise
        except ApiError as exc:
            event({"step": name, "api_attempts": attempts, "status": "fallback", "reason": str(exc)})
            result = mock_result(name, context)
            origin = "deterministic_local_fallback"
        _validate_model(name, result, review_ids, product_ids)
        return {"origin": origin, "result": result, "api_attempts": attempts}

    try:
        brand = step("brand_profile", {"request": request}, lambda: {
            "brand": "清波 ClearWave", "type": "课程虚构品牌",
            "voice": "稳健、透明、说明测试条件", "focal_competition_brand": "Skullcandy",
            "boundary": "清波不是 Skullcandy 官方品牌；策划是课程草案。"},
            ["src/brand_voice.py"])

        def consumer_action():
            nonlocal reviews, review_ids
            source = ROOT / "data" / "raw" / "reviews.csv"
            annotations = ROOT / "data" / "processed" / "semantic_annotations.json"
            product = ROOT / "data" / "processed" / "clean_data.csv"
            out = run_dir / "consumer_outputs"
            summary = consumer.run(source, annotations, product, out, run_dir / "clean_reviews.csv")
            reviews = json.loads(project_path(out / "encoded_reviews.json").read_text(encoding="utf-8"))["records"]
            review_ids = {r["review_id"] for r in reviews}
            pain = pd.read_csv(project_path(out / "pain_ranking.csv"), encoding="utf-8-sig").head(4).to_dict("records")
            return {"component": "experiment4.consumer_insight_engine.run", "summary": summary,
                    "top_pains": pain, "encoded_file": str((out / "encoded_reviews.json").relative_to(run_dir)),
                    "raw_review_sha256": _hash(source)}

        consumer_result = step("consumer_insight", {"raw": "data/raw/reviews.csv", "annotations": "data/processed/semantic_annotations.json"},
                               consumer_action, ["data/raw/reviews.csv", "data/processed/semantic_annotations.json"])

        def competition_action():
            nonlocal products, product_ids
            products, comp_reviews = competition.load_inputs(
                ROOT / "data" / "processed" / "clean_data.csv",
                run_dir / "consumer_outputs" / "encoded_reviews.json")
            product_ids = set(products["listing_id"].astype(str))
            result = competition.calculate(products, comp_reviews, "Skullcandy")
            sens = competition.sensitivity(products, comp_reviews, "Skullcandy")
            competition.write_outputs(result, sens, run_dir / "competition_outputs",
                                      ROOT / "data" / "processed" / "clean_data.csv",
                                      run_dir / "consumer_outputs" / "encoded_reviews.json")
            return {"component": "experiment5.competitive_intelligence.calculate",
                    "ranked": result["scores"].loc[result["scores"]["rank_status"].eq("ranked"),
                                                  ["competitor", "rank", "threat_index"]].to_dict("records"),
                    "scores_file": "competition_outputs/scores.csv"}

        competitive_result = step("competitive_analysis", {"focal": "Skullcandy", "encoded_file": consumer_result["encoded_file"]},
                                  competition_action, ["data/processed/clean_data.csv", "consumer_outputs/encoded_reviews.json"])

        def content_action():
            nonlocal briefs
            inputs = gap.load_inputs(run_dir / "consumer_outputs" / "encoded_reviews.json",
                                     ROOT / "data" / "processed" / "clean_data.csv",
                                     ROOT / "data" / "processed" / "selling_points.csv",
                                     run_dir / "competition_outputs" / "scores.csv")
            result = gap.calculate(*inputs)
            briefs = result["briefs"]
            gap.write_outputs(result, run_dir / "content_outputs", [
                run_dir / "consumer_outputs" / "encoded_reviews.json",
                ROOT / "data" / "processed" / "clean_data.csv",
                ROOT / "data" / "processed" / "selling_points.csv",
                run_dir / "competition_outputs" / "scores.csv"])
            return {"component": "experiment6.content_opportunity.calculate",
                    "opportunity_count": result["summary"]["opportunity_count"],
                    "brief_count": len(briefs), "top_theme": briefs[0]["theme"],
                    "brief_file": "content_outputs/strategy_briefs.json"}

        content_result = step("content_gap", {"scores_file": competitive_result["scores_file"],
                                               "encoded_file": consumer_result["encoded_file"]},
                              content_action, ["competition_outputs/scores.csv", "consumer_outputs/encoded_reviews.json",
                                               "data/processed/selling_points.csv"])

        def voice_action():
            results = [{"theme": b["theme"], "errors": brand_voice.validate_brief(b)} for b in briefs]
            if any(row["errors"] for row in results):
                raise WorkflowError("Brand Voice 检查失败。")
            return {"component": "experiment6.brand_voice.validate_brief",
                    "checked_briefs": len(results), "passed": len(results), "results": results}

        voice_result = step("brand_voice", {"brief_file": content_result["brief_file"]}, voice_action,
                            ["content_outputs/strategy_briefs.json", "src/brand_voice.py"])

        context = {"brand": brand, "consumer": consumer_result, "competition": competitive_result,
                   "content_gap": content_result, "brand_voice": voice_result, "briefs": briefs}
        target = step("target_consumer", {"top_theme": briefs[0]["theme"], "api": api_url},
                      lambda: model_action("target_consumer", context),
                      ["content_outputs/strategy_briefs.json", "consumer_outputs/encoded_reviews.json"])
        context["target_consumer"] = target["result"]
        theme = step("communication_theme", {"target_consumer": target["result"]["segment"], "api": api_url},
                     lambda: model_action("communication_theme", context),
                     ["content_outputs/strategy_briefs.json", "src/brand_voice.py"])
        context["communication_theme"] = theme["result"]
        channels = step("channel_plan", {"communication_theme": theme["result"]["theme"], "api": api_url},
                        lambda: model_action("channel_plan", context),
                        ["content_outputs/strategy_briefs.json", "07_communication_theme.json"])
        context["channel_plan"] = channels["result"]
        event({"step": "human_review", "status": "pending", "reason": "产品事实、预算、渠道资源及对外发布需人工审核"})
        campaign = step("campaign", {"channel_plan": channels["result"], "human_review": "pending", "api": api_url},
                        lambda: model_action("campaign", context),
                        ["consumer_outputs/encoded_reviews.json", "competition_outputs/evidence.csv",
                         "content_outputs/evidence_record.csv", "content_outputs/strategy_briefs.json"])
        state["status"] = "draft_pending_human_review"
        _write_json(run_dir / "campaign_draft.json", campaign["result"])
        _write_json(run_dir / "state.json", state)
        event({"step": "workflow", "status": state["status"]})
        return {"run_dir": str(run_dir), "status": state["status"], "campaign": campaign["result"],
                "steps_completed": len(state["steps"])}
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
        _write_json(run_dir / "state.json", state)
        event({"step": "workflow", "status": "failed", "error": str(exc)})
        raise WorkflowError(f"运行 {run_id} 失败：{exc}") from exc
    finally:
        if local_server is not None:
            local_server.shutdown()
            local_server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Traceable Bluetooth earbud marketing workflow")
    parser.add_argument("request", nargs="?", default=DEFAULT_REQUEST)
    parser.add_argument("--api-url", help="Optional HTTP JSON endpoint; default is local mock")
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    result = run_workflow(args.request, api_url=args.api_url, timeout=args.timeout, retries=args.retries)
    print(json.dumps({"run_dir": result["run_dir"], "status": result["status"],
                      "steps_completed": result["steps_completed"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

