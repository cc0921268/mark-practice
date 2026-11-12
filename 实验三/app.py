"""Local upload interface for the reproducible headphone cleaning pipeline."""

import hashlib
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from src.clean import CleanError, clean_bytes, csv_bytes

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 5 * 1024 * 1024


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
        elif self.path == "/api/quality":
            file = ROOT / "outputs" / "quality_statistics.json"
            self.send_bytes(200, file.read_bytes(), "application/json; charset=utf-8")
        elif self.path == "/api/download-clean":
            file = ROOT / "data" / "processed" / "clean_data.csv"
            self.send_bytes(200, file.read_bytes(), "text/csv; charset=utf-8")
        else:
            self.send_json(404, {"error": "页面不存在。"})

    def do_POST(self) -> None:
        if self.path != "/api/clean-upload":
            self.send_json(404, {"error": "接口不存在。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if not 1 <= size <= MAX_BYTES:
            self.send_json(400, {"error": "请选择不超过 5 MB 的 CSV 文件。"})
            return
        source = unquote(self.headers.get("X-Data-Source", "")).strip()
        collected = self.headers.get("X-Collection-Date", "").strip()
        name = unquote(self.headers.get("X-File-Name", "upload.csv")).strip()
        if not source:
            self.send_json(400, {"error": "请填写数据来源。"})
            return
        try:
            datetime.strptime(collected, "%Y-%m-%d")
        except ValueError:
            self.send_json(400, {"error": "请填写有效的采集日期（YYYY-MM-DD）。"})
            return
        if not name.lower().endswith(".csv"):
            self.send_json(400, {"error": "请上传 .csv 文件。"})
            return
        raw = self.rfile.read(size)
        now = datetime.now(timezone.utc)
        digest = hashlib.sha256(raw).hexdigest()
        file_id = now.strftime("%Y%m%dT%H%M%S%fZ") + "_" + digest[:12]
        raw_dir = ROOT / "data" / "raw" / "uploads"
        processed_dir = ROOT / "data" / "processed" / "uploads"
        raw_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{file_id}.csv"
        with raw_path.open("xb") as handle:
            handle.write(raw)
        log = {"id": file_id, "source": source, "collection_date": collected,
               "original_filename": Path(name).name, "uploaded_at_utc": now.isoformat(),
               "raw_file": str(raw_path.relative_to(ROOT)), "raw_sha256": digest}
        try:
            rows, quality, changes = clean_bytes(raw)
            processed_path = processed_dir / f"{file_id}.csv"
            with processed_path.open("xb") as handle:
                handle.write(csv_bytes(rows))
            log.update({"status": "success", "processed_file": str(processed_path.relative_to(ROOT)),
                        "clean_rows": len(rows)})
            self.send_json(200, {"metadata": log, "quality": quality,
                                 "changes": changes, "preview": rows[:10]})
        except CleanError as exc:
            log.update({"status": "validation_error", "error": str(exc)})
            self.send_json(400, {"error": str(exc), "metadata": log})
        finally:
            with (ROOT / "outputs" / "upload_log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("MARKETING_PIPELINE_PORT", "8503"))
    print(f"营销数据清洗已启动：http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

