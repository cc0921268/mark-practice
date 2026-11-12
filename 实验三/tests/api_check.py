"""Check the local upload interface without external test packages."""

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
environment["MARKETING_PIPELINE_PORT"] = str(PORT)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=environment,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def upload(raw: bytes, name: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/api/clean-upload", data=raw, method="POST",
        headers={"Content-Type": "text/csv", "X-Data-Source": urllib.parse.quote("公开数据抽样"),
                 "X-Collection-Date": "2026-11-10", "X-File-Name": name})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


try:
    for _ in range(50):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1).close()
            break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)
    else:
        raise RuntimeError("本地服务未启动")
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/download-clean") as response:
        assert response.read() == (ROOT / "data" / "processed" / "clean_data.csv").read_bytes()
    sample = (ROOT / "data" / "sample" / "first_50.csv").read_bytes()
    status, result = upload(sample, "first_50.csv")
    assert status == 200 and result["quality"]["raw_rows"] == 50
    assert result["quality"]["clean_rows"] > 0
    saved = ROOT / result["metadata"]["raw_file"]
    assert saved.read_bytes() == sample
    assert hashlib.sha256(saved.read_bytes()).hexdigest() == result["metadata"]["raw_sha256"]
    status, error = upload(b"listing_id,title\n1,test\n", "missing.csv")
    assert status == 400 and "缺少必需字段" in error["error"]
    assert (ROOT / error["metadata"]["raw_file"]).read_bytes() == b"listing_id,title\n1,test\n"
    print("API check: download, upload, quality, missing field, raw preservation OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

