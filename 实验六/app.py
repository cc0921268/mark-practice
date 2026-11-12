"""Local Content Gap and Brand Voice dashboard with isolated uploads."""

import base64
import binascii
import hashlib
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.brand_voice import BANNED, BRAND_NAME, PREFERRED, validate_text
from src.content_opportunity import (
    DataError, ENCODED, OUTPUTS, PRODUCTS, SCORES, SELLING,
    calculate, load_inputs, write_outputs,
)

ROOT = Path(__file__).resolve().parent
MAX_BODY = 8 * 1024 * 1024


def payload(result: dict) -> dict:
    return {"theme_matrix": json.loads(result["theme_matrix"].to_json(orient="records", force_ascii=False)),
            "competitor_brand_coverage": json.loads(result["competitor_brand_coverage"].to_json(orient="records", force_ascii=False)),
            "evidence_record": json.loads(result["evidence_record"].to_json(orient="records", force_ascii=False)),
            "briefs": result["briefs"], "summary": result["summary"],
            "brand_voice": {"name": BRAND_NAME, "preferred": PREFERRED, "banned": BANNED}}


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
        elif self.path == "/api/dashboard":
            self.send_json(200, payload(calculate(*load_inputs())))
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path not in ("/api/upload", "/api/check-voice"):
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= MAX_BODY:
                raise DataError("上传内容不能超过 8 MB。")
            request = json.loads(self.rfile.read(size))
            if self.path == "/api/check-voice":
                text = request.get("text", "")
                errors = validate_text(text)
                self.send_json(200, {"valid": not errors, "errors": errors})
                return
            source = str(request.get("source", "")).strip()
            collected = str(request.get("collection_date", "")).strip()
            filename = str(request.get("filename", "encoded_reviews.json")).strip()
            if not source:
                raise DataError("请填写数据来源。")
            try:
                datetime.strptime(collected, "%Y-%m-%d")
            except ValueError as exc:
                raise DataError("请填写有效的采集日期（YYYY-MM-DD）。") from exc
            if not filename.lower().endswith(".json"):
                raise DataError("请上传 JSON 编码文件。")
            raw = base64.b64decode(request["encoded_base64"], validate=True)
            if len(raw) > 5 * 1024 * 1024:
                raise DataError("编码 JSON 不能超过 5 MB。")
        except (ValueError, KeyError, TypeError, binascii.Error, DataError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        now = datetime.now(timezone.utc)
        file_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "_" + hashlib.sha256(raw).hexdigest()[:12]
        raw_dir = ROOT / "data" / "raw" / "uploads"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{file_id}.json"
        with raw_path.open("xb") as handle:
            handle.write(raw)
        log = {"id": file_id, "source": source, "collection_date": collected,
               "original_filename": Path(filename).name, "uploaded_at_utc": now.isoformat(),
               "raw_file": str(raw_path.relative_to(ROOT)), "raw_sha256": hashlib.sha256(raw).hexdigest()}
        try:
            inputs = load_inputs(raw_path, PRODUCTS, SELLING, SCORES)
            result = calculate(*inputs)
            output_dir = OUTPUTS / "runs" / file_id
            write_outputs(result, output_dir, [raw_path, PRODUCTS, SELLING, SCORES])
            log.update({"status": "success", "output_dir": str(output_dir.relative_to(ROOT))})
            response = payload(result)
            response["upload_metadata"] = log
            self.send_json(200, response)
        except (DataError, UnicodeDecodeError) as exc:
            log.update({"status": "validation_error", "error": str(exc)})
            self.send_json(400, {"error": str(exc), "metadata": log})
        finally:
            with (OUTPUTS / "upload_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("CONTENT_GAP_PORT", "8506"))
    print(f"Content Gap 与 Brand Voice：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

