"""Check UI upload lifecycle and saved raw request."""

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
    port = sock.getsockname()[1]
env = os.environ.copy()
env["MARKETING_WORKFLOW_PORT"] = str(port)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def post(value):
    raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(f"http://127.0.0.1:{port}/api/run", data=raw,
                                     method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.load(response), raw
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc), raw


try:
    for _ in range(80):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1).close()
            break
        except urllib.error.URLError:
            time.sleep(.1)
    status, error, _ = post({"request": "给蓝牙耳机设计一次新品推广", "source": "", "collection_date": "2026-11-10"})
    assert status == 400 and "输入来源" in error["error"]
    status, result, raw = post({"request": "给蓝牙耳机设计一次新品推广",
                                "source": "课程个人作业", "collection_date": "2026-11-10"})
    assert status == 200 and result["result"]["steps_completed"] == 9
    assert result["result"]["campaign"]["approval_status"] == "pending_human_review"
    assert (ROOT / result["upload"]["raw_file"]).read_bytes() == raw
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/latest") as response:
        latest = json.load(response)
    assert latest["state"]["status"] == "draft_pending_human_review"
    print("UI API check: validation, nine steps, raw input, pending review OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

