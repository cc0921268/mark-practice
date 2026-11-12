"""Local marketing CSV dashboard. Run with: python app.py"""

import hashlib
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from src.analysis import DataError, analyse_csv

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
MAX_BYTES = 5 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, obj: dict) -> None:
        self.send_bytes(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_bytes(200, (ROOT / "src" / "ui.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path != "/api/analyse":
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if size < 1 or size > MAX_BYTES:
            self.send_json(400, {"error": "请选择不超过 5 MB 的 CSV 文件。"})
            return
        source = unquote(self.headers.get("X-Data-Source", "")).strip()
        collected = self.headers.get("X-Collection-Date", "").strip()
        filename = unquote(self.headers.get("X-File-Name", "upload.csv")).strip()
        if not source:
            self.send_json(400, {"error": "请填写数据来源。"})
            return
        try:
            datetime.strptime(collected, "%Y-%m-%d")
        except ValueError:
            self.send_json(400, {"error": "请填写有效的采集日期（YYYY-MM-DD）。"})
            return
        if not filename.lower().endswith(".csv"):
            self.send_json(400, {"error": "请上传 .csv 文件。"})
            return
        raw = self.rfile.read(size)
        now = datetime.now(timezone.utc)
        file_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "_" + hashlib.sha256(raw).hexdigest()[:12]
        RAW.mkdir(parents=True, exist_ok=True)
        PROCESSED.mkdir(parents=True, exist_ok=True)
        OUTPUTS.mkdir(parents=True, exist_ok=True)
        raw_path = RAW / f"{file_id}.csv"
        with raw_path.open("xb") as handle:
            handle.write(raw)
        record = {"id": file_id, "original_filename": Path(filename).name,
                  "source": source, "collection_date": collected,
                  "field_uses": {"brand": "品牌分组及筛选", "price": "平均价格",
                                 "rating": "平均评分", "product": "保留但本实验不分析",
                                 "sales": "保留但本实验不分析"},
                  "upload_time_utc": now.isoformat(), "raw_file": str(raw_path.relative_to(ROOT)),
                  "sha256": hashlib.sha256(raw).hexdigest()}
        try:
            result = analyse_csv(raw)
            processed_path = PROCESSED / f"{file_id}.json"
            with processed_path.open("x", encoding="utf-8") as handle:
                json.dump({"metadata": record, "analysis": result}, handle, ensure_ascii=False, indent=2)
            record.update({"status": "success", "processed_file": str(processed_path.relative_to(ROOT)),
                           "valid_rows": result["valid_rows"], "skipped_rows": result["skipped_rows"]})
            self.send_json(200, {"metadata": record, "analysis": result})
        except DataError as exc:
            record.update({"status": "validation_error", "error": str(exc)})
            self.send_json(400, {"error": str(exc), "metadata": record})
        finally:
            with (OUTPUTS / "processing_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("MARKETING_OS_PORT", "8501"))
    print(f"营销数据分析已启动：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
