"""End-to-end upload check using only the Python standard library."""

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    PORT = sock.getsockname()[1]
environment = os.environ.copy()
environment["CONSUMER_INSIGHT_PORT"] = str(PORT)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=environment,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def upload(name):
    raw = (ROOT / "data" / "sample" / name).read_bytes()
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/api/analyze", data=raw, method="POST",
        headers={"Content-Type": "text/csv", "X-Data-Source": urllib.parse.quote("课程自建样例"),
                 "X-Collection-Date": "2026-11-10", "X-File-Name": name})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.load(response), raw
    except urllib.error.HTTPError as error:
        return error.code, json.load(error), raw


try:
    for _ in range(50):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1).close()
            break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    else:
        raise RuntimeError("本地服务未启动")

    first_status, first, raw = upload("reviews.csv")
    assert first_status == 200 and len(first["analysis"]["records"]) == 10
    assert (ROOT / first["metadata"]["raw_file"]).read_bytes() == raw
    assert (ROOT / first["metadata"]["processed_file"]).exists()
    assert hashlib.sha256(raw).hexdigest() == first["metadata"]["sha256"]

    second_status, second, _ = upload("reviews.csv")
    assert second_status == 200 and first["analysis"] == second["analysis"]
    assert first["metadata"]["raw_file"] != second["metadata"]["raw_file"]

    missing_status, missing, missing_raw = upload("missing_field.csv")
    assert missing_status == 400 and "review" in missing["error"]
    assert (ROOT / missing["metadata"]["raw_file"]).read_bytes() == missing_raw
    print("API check: upload, 10 records, repeatability, missing field, raw preservation OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

