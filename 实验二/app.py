"""HTTP entry point for the GitHub Skill CSV adapter."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from src.consumer_insight_adapter import AdapterError, analyze_reviews_csv

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (Path(__file__).parent / "src" / "ui.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        if self.path != "/api/analyze":
            self.send_error(404); return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= 5 * 1024 * 1024:
                raise AdapterError("CSV size must be between 1B and 5MB")
            result = analyze_reviews_csv(self.rfile.read(size), source_name=self.headers.get("X-File-Name", "reviews.csv"))
            body = json.dumps(result, ensure_ascii=False).encode("utf-8"); self.send_response(200)
        except (ValueError, AdapterError) as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8"); self.send_response(400)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8762), Handler).serve_forever()
