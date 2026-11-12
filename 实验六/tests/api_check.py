"""Check local page, Brand Voice endpoint, upload, and raw preservation."""

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
env = os.environ.copy()
env["CONTENT_GAP_PORT"] = str(PORT)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def post(route: str, value: dict):
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}{route}",
                                     data=json.dumps(value).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


try:
    for _ in range(70):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1).close()
            break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(.1)
    else:
        raise RuntimeError("本地服务未启动")
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/dashboard") as response:
        dashboard = json.load(response)
    assert dashboard["summary"]["opportunity_count"] == 6
    assert len(dashboard["briefs"]) == 6
    assert dashboard["summary"]["competitor_title_sample_size"] == 13
    status, good = post("/api/check-voice", {"text": "在统一音量条件下实测续航，并说明充电步骤。"})
    assert status == 200 and good["valid"]
    status, bad = post("/api/check-voice", {"text": "永久零故障，行业第一。"})
    assert status == 200 and not bad["valid"]
    original = (ROOT / "data" / "processed" / "encoded_reviews.json").read_bytes()
    request = {"filename": "encoded_reviews.json", "source": "实验四真实评论编码副本",
               "collection_date": "2026-11-10", "encoded_base64": base64.b64encode(original).decode("ascii")}
    status, uploaded = post("/api/upload", request)
    assert status == 200 and uploaded["summary"]["brief_count"] == 6
    saved = ROOT / uploaded["upload_metadata"]["raw_file"]
    assert saved.read_bytes() == original
    assert hashlib.sha256(saved.read_bytes()).hexdigest() == uploaded["upload_metadata"]["raw_sha256"]
    assert (ROOT / uploaded["upload_metadata"]["output_dir"] / "strategy_briefs.json").exists()
    print("API check: Dashboard, Voice checker, upload, raw preservation OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

