"""End-to-end local Dashboard and upload verification."""

import base64
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    PORT = sock.getsockname()[1]
environment = os.environ.copy()
environment["CONSUMER_DASHBOARD_PORT"] = str(PORT)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=environment,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def post(csv_path: Path, codes_path: Path):
    raw = csv_path.read_bytes()
    payload = {"filename": csv_path.name, "source": "课程自建边界样例",
               "collection_date": "2026-11-10",
               "reviews_base64": base64.b64encode(raw).decode("ascii"),
               "annotations": json.loads(codes_path.read_text(encoding="utf-8"))}
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/analyze-upload",
                                     data=json.dumps(payload).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.load(response), raw
    except urllib.error.HTTPError as error:
        return error.code, json.load(error), raw


try:
    for _ in range(70):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1).close()
            break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    else:
        raise RuntimeError("本地 Dashboard 未启动")
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/dashboard") as response:
        dashboard = json.load(response)
    assert dashboard["summary"]["review_sample_size"] == 30
    assert dashboard["pain_ranking"][0]["pain_tag"] == "device_failure"
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/encoded") as response:
        assert len(json.load(response)["records"]) == 30

    sample = ROOT / "data" / "sample"
    status, result, raw = post(sample / "case_normal.csv", sample / "case_normal_codes.json")
    assert status == 200 and result["summary"]["review_sample_size"] == 3
    saved = ROOT / result["upload_metadata"]["raw_file"]
    assert saved.read_bytes() == raw
    assert hashlib.sha256(raw).hexdigest() == result["upload_metadata"]["raw_sha256"]

    status, error, raw = post(sample / "case_normal.csv", sample / "case_fabricated_quote.json")
    assert status == 400 and "证据不是原评论子串" in error["error"]
    assert (ROOT / error["metadata"]["raw_file"]).read_bytes() == raw
    status, error, raw = post(sample / "case_missing_field.csv", sample / "case_normal_codes.json")
    assert status == 400 and "缺少字段" in error["error"]
    assert (ROOT / error["metadata"]["raw_file"]).read_bytes() == raw
    print("API check: Dashboard, 3-row upload, missing field, quote rejection, raw preservation OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

