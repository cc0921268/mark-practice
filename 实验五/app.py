"""Local competition dashboard and isolated upload workflow."""

import base64
import binascii
import hashlib
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pandas as pd

from src.competitive_intelligence import (
    DataError, DEFAULT_FOCAL, OUTPUTS, PRODUCTS, REVIEWS,
    calculate, load_inputs, sensitivity, write_outputs,
)

ROOT = Path(__file__).resolve().parent
MAX_BODY = 10 * 1024 * 1024
TABLE_NAMES = ("scores", "evidence", "product_structure", "price_bands", "brand_ratings",
               "selling_points", "market_gap_segments", "sensitivity")


def _records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.where(pd.notna(frame), None).to_json(orient="records", force_ascii=False))


def _payload(result: dict, sensitivity_frame: pd.DataFrame) -> dict:
    data = {name: _records(value) for name, value in result.items() if isinstance(value, pd.DataFrame)}
    data["sensitivity"] = _records(sensitivity_frame)
    data["summary"] = result["summary"]
    return data


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
            products, reviews = load_inputs()
            result = calculate(products, reviews, DEFAULT_FOCAL)
            self.send_json(200, _payload(result, sensitivity(products, reviews, DEFAULT_FOCAL)))
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path not in ("/api/recalculate", "/api/upload"):
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= MAX_BODY:
                raise DataError("上传内容必须为 1–10 MB 以内的 JSON。")
            request = json.loads(self.rfile.read(size))
            focal = str(request.get("focal", DEFAULT_FOCAL)).strip()
            if self.path == "/api/recalculate":
                products, reviews = load_inputs()
                result = calculate(products, reviews, focal)
                self.send_json(200, _payload(result, sensitivity(products, reviews, focal)))
                return
            source = str(request.get("source", "")).strip()
            collected = str(request.get("collection_date", "")).strip()
            if not source:
                raise DataError("请填写数据来源。")
            try:
                datetime.strptime(collected, "%Y-%m-%d")
            except ValueError as exc:
                raise DataError("请填写有效的采集日期（YYYY-MM-DD）。") from exc
            product_bytes = base64.b64decode(request["products_base64"], validate=True)
            review_bytes = base64.b64decode(request["encoded_reviews_base64"], validate=True)
            if len(product_bytes) > 5 * 1024 * 1024 or len(review_bytes) > 5 * 1024 * 1024:
                raise DataError("单个文件不能超过 5 MB。")
        except (ValueError, TypeError, KeyError, binascii.Error, DataError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        now = datetime.now(timezone.utc)
        file_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "_" + hashlib.sha256(product_bytes + review_bytes).hexdigest()[:12]
        raw_dir = ROOT / "data" / "raw" / "uploads"
        raw_dir.mkdir(parents=True, exist_ok=True)
        product_path = raw_dir / f"{file_id}_products.csv"
        review_path = raw_dir / f"{file_id}_encoded_reviews.json"
        with product_path.open("xb") as handle:
            handle.write(product_bytes)
        with review_path.open("xb") as handle:
            handle.write(review_bytes)
        log = {"id": file_id, "source": source, "collection_date": collected,
               "uploaded_at_utc": now.isoformat(),
               "raw_product_file": str(product_path.relative_to(ROOT)),
               "raw_encoded_file": str(review_path.relative_to(ROOT)),
               "product_sha256": hashlib.sha256(product_bytes).hexdigest(),
               "encoded_sha256": hashlib.sha256(review_bytes).hexdigest()}
        try:
            products, reviews = load_inputs(product_path, review_path)
            result = calculate(products, reviews, focal)
            sens = sensitivity(products, reviews, focal)
            output_dir = OUTPUTS / "runs" / file_id
            write_outputs(result, sens, output_dir, product_path, review_path)
            log.update({"status": "success", "output_dir": str(output_dir.relative_to(ROOT))})
            response = _payload(result, sens)
            response["upload_metadata"] = log
            self.send_json(200, response)
        except (DataError, UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            log.update({"status": "validation_error", "error": str(exc)})
            self.send_json(400, {"error": str(exc), "metadata": log})
        finally:
            with (OUTPUTS / "upload_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("COMPETITIVE_DASHBOARD_PORT", "8505"))
    print(f"竞品 Dashboard：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

