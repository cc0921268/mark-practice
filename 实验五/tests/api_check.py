"""End-to-end check of dashboard, reweighting view, and upload preservation."""

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
env["COMPETITIVE_DASHBOARD_PORT"] = str(PORT)
server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def post(path: str, payload: dict):
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}",
                                     data=json.dumps(payload).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


try:
    for _ in range(80):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1).close()
            break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(.1)
    else:
        raise RuntimeError("Dashboard 未启动")
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/dashboard") as response:
        baseline = json.load(response)
    assert baseline["summary"]["focal_brand"] == "Skullcandy"
    assert baseline["scores"][0]["competitor"] == "Sennheiser"
    assert len(baseline["evidence"]) == 20
    status, alternate = post("/api/recalculate", {"focal": "Sennheiser"})
    assert status == 200 and alternate["summary"]["focal_brand"] == "Sennheiser"

    products = (ROOT / "data" / "processed" / "clean_data.csv").read_bytes()
    reviews = (ROOT / "data" / "processed" / "encoded_reviews.json").read_bytes()
    payload = {"focal": "Skullcandy", "source": "实验三与实验四已核验样本",
               "collection_date": "2026-11-10",
               "products_base64": base64.b64encode(products).decode("ascii"),
               "encoded_reviews_base64": base64.b64encode(reviews).decode("ascii")}
    status, uploaded = post("/api/upload", payload)
    assert status == 200 and uploaded["scores"][0]["competitor"] == "Sennheiser"
    meta = uploaded["upload_metadata"]
    assert (ROOT / meta["raw_product_file"]).read_bytes() == products
    assert (ROOT / meta["raw_encoded_file"]).read_bytes() == reviews
    assert hashlib.sha256(products).hexdigest() == meta["product_sha256"]
    assert (ROOT / meta["output_dir"] / "scores.csv").exists()
    print("API check: Dashboard, focal recalculation, upload, raw preservation OK")
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()

