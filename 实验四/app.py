"""Local dashboard; uploaded codes are supplied by AI/humans, never computed here."""

import base64
import binascii
import csv
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pandas as pd

from src.consumer_insight_engine import InputError, run

ROOT = Path(__file__).resolve().parent
MAX_BODY = 10 * 1024 * 1024
TABLES = ("pain_ranking", "sentiment_distribution", "brand_comparison", "product_snapshot_by_date")


def table(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def dashboard_payload(folder: Path) -> dict:
    payload = {name: table(folder / f"{name}.csv") for name in TABLES}
    payload["summary"] = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    payload["encoded"] = json.loads((folder / "encoded_reviews.json").read_text(encoding="utf-8"))
    return payload


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: dict) -> None:
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_bytes(200, (ROOT / "src" / "ui.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/dashboard":
            self.send_json(200, dashboard_payload(ROOT / "outputs"))
        elif self.path == "/api/encoded":
            self.send_bytes(200, (ROOT / "outputs" / "encoded_reviews.json").read_bytes(),
                            "application/json; charset=utf-8")
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path != "/api/analyze-upload":
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if not 1 <= size <= MAX_BODY:
            self.send_json(400, {"error": "上传内容不能超过 10 MB。"})
            return
        try:
            request = json.loads(self.rfile.read(size))
            source = str(request.get("source", "")).strip()
            collected = str(request.get("collection_date", "")).strip()
            filename = str(request.get("filename", "reviews.csv")).strip()
            if not source:
                raise InputError("请填写数据来源。")
            try:
                datetime.strptime(collected, "%Y-%m-%d")
            except ValueError as exc:
                raise InputError("请填写有效的采集日期（YYYY-MM-DD）。") from exc
            if not filename.lower().endswith(".csv"):
                raise InputError("请上传 CSV 评论文件。")
            raw = base64.b64decode(request["reviews_base64"], validate=True)
            annotations = request["annotations"]
            if not isinstance(annotations, list):
                raise InputError("语义编码必须为 JSON 数组。")
        except (KeyError, ValueError, TypeError, binascii.Error, InputError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        now = datetime.now(timezone.utc)
        file_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "_" + hashlib.sha256(raw).hexdigest()[:12]
        raw_dir = ROOT / "data" / "raw" / "uploads"
        processed_dir = ROOT / "data" / "processed" / "uploads"
        output_dir = ROOT / "outputs" / "runs" / file_id
        for folder in (raw_dir, processed_dir, output_dir):
            folder.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{file_id}.csv"
        annotations_path = raw_dir / f"{file_id}_annotations.json"
        with raw_path.open("xb") as handle:
            handle.write(raw)
        with annotations_path.open("x", encoding="utf-8") as handle:
            json.dump(annotations, handle, ensure_ascii=False, indent=2)
        log = {"id": file_id, "source": source, "collection_date": collected,
               "original_filename": Path(filename).name,
               "raw_file": str(raw_path.relative_to(ROOT)),
               "annotations_file": str(annotations_path.relative_to(ROOT)),
               "raw_sha256": hashlib.sha256(raw).hexdigest(),
               "uploaded_at_utc": now.isoformat()}
        try:
            summary = run(raw_path, annotations_path, ROOT / "data" / "processed" / "clean_data.csv",
                          output_dir, processed_dir / f"{file_id}_clean_reviews.csv")
            log.update({"status": "success", "output_dir": str(output_dir.relative_to(ROOT)),
                        "review_count": summary["review_sample_size"]})
            payload = dashboard_payload(output_dir)
            payload["upload_metadata"] = log
            self.send_json(200, payload)
        except (InputError, ValueError, UnicodeDecodeError, pd.errors.ParserError,
                pd.errors.EmptyDataError) as exc:
            log.update({"status": "validation_error", "error": str(exc)})
            self.send_json(400, {"error": str(exc), "metadata": log})
        finally:
            with (ROOT / "outputs" / "upload_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("CONSUMER_DASHBOARD_PORT", "8504"))
    print(f"消费者洞察 Dashboard：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

