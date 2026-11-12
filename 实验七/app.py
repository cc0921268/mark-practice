"""Local upload and workflow status page."""

import json
import os
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.marketing_workflow import WorkflowError, run_workflow

ROOT = Path(__file__).resolve().parent
MAX_BODY = 32 * 1024


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, value: dict) -> None:
        self.send_bytes(status, json.dumps(value, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_bytes(200, (ROOT / "src" / "ui.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/latest":
            runs = sorted((ROOT / "outputs" / "runs").glob("*/state.json"), reverse=True)
            if not runs:
                self.send_json(200, {"status": "not_run"})
            else:
                state = json.loads(runs[0].read_text(encoding="utf-8"))
                campaign_path = runs[0].parent / "campaign_draft.json"
                self.send_json(200, {"state": state, "campaign": json.loads(campaign_path.read_text(encoding="utf-8")) if campaign_path.exists() else None})
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= MAX_BODY:
                raise ValueError("请求不能超过 32 KB。")
            raw = self.rfile.read(size)
            request = json.loads(raw)
            text = str(request.get("request", "")).strip()
            source = str(request.get("source", "")).strip()
            date = str(request.get("collection_date", "")).strip()
            if not text:
                raise ValueError("请填写推广需求。")
            if not source:
                raise ValueError("请填写输入来源。")
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("请填写有效采集日期（YYYY-MM-DD）。") from exc
        except (ValueError, TypeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        upload_dir = ROOT / "data" / "raw" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        upload_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]
        raw_path = upload_dir / f"{upload_id}.json"
        with raw_path.open("xb") as handle:
            handle.write(raw)
        log = {"upload_id": upload_id, "source": source, "collection_date": date,
               "raw_file": str(raw_path.relative_to(ROOT)), "status": "processing"}
        try:
            result = run_workflow(text)
            log.update({"status": result["status"], "run_dir": result["run_dir"]})
            self.send_json(200, {"upload": log, "result": result})
        except WorkflowError as exc:
            log.update({"status": "failed", "error": str(exc)})
            self.send_json(500, {"error": str(exc), "upload": log})
        finally:
            with (ROOT / "outputs" / "upload_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("MARKETING_WORKFLOW_PORT", "8507"))
    print(f"营销 Workflow：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

