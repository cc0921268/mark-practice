"""Import a pinned public GitHub dataset snapshot into a de-identified CSV."""

import argparse
import base64
import csv
import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "Haseeb-U/ebay-headphones-market-dataset"
COMMIT = "18fb2f845f9d0ff7a6659884c6d9b6fae2c7111c"
BLOB_SHA = "a652532a226278f4cba856efdcd97b2cf62cf2d7"
API_URL = f"https://api.github.com/repos/{REPO}/git/blobs/{BLOB_SHA}"
RAW = ROOT / "data" / "raw" / "raw_data.csv"
SAMPLE = ROOT / "data" / "sample" / "first_50.csv"
FIELDS = ("listing_id", "title", "brand", "price", "currency", "rating",
          "reviews_count", "watchers_count", "scrape_timestamp", "wireless", "bluetooth_evidence")
CORE = ("listing_id", "title", "brand", "price", "rating", "reviews_count", "scrape_timestamp")


def source_bytes(blob_json: Path | None) -> bytes:
    if blob_json is None:
        request = urllib.request.Request(API_URL, headers={"User-Agent": "marketing-experiment03"})
        with urllib.request.urlopen(request, timeout=120) as response:
            blob = json.load(response)
    else:
        blob = json.loads(blob_json.read_text(encoding="utf-8"))
    if blob.get("sha") != BLOB_SHA or blob.get("encoding") != "base64":
        raise ValueError("来源文件版本或编码与固定版本不符。")
    raw = base64.b64decode(blob["content"])
    actual_blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if actual_blob != BLOB_SHA:
        raise ValueError("来源文件校验失败。")
    return raw


def select_rows(source: bytes) -> list[dict]:
    reader = csv.DictReader(io.StringIO(source.decode("utf-8-sig"), newline=""))
    missing = [field for field in FIELDS[:-1] if field not in (reader.fieldnames or [])]
    if missing:
        raise ValueError("来源缺少字段：" + ", ".join(missing))
    selected = []
    for row in reader:
        title = (row.get("title") or "").lower()
        explicit = "bluetooth" in title
        proxy = "wireless" in title and (row.get("wireless") or "").strip() == "1.0"
        if not (explicit or proxy):
            continue
        if not all((row.get(field) or "").strip() for field in CORE):
            continue
        record = {field: (row.get(field) or "").strip() for field in FIELDS[:-1]}
        record["bluetooth_evidence"] = "explicit_title" if explicit else "wireless_flag_proxy"
        selected.append(record)
        if len(selected) == 480:
            break
    if len(selected) != 480:
        raise ValueError(f"来源仅满足 {len(selected)} 条，未达到固定抽取数 480。")
    return selected


def write_csv_exclusive(path: Path, rows: list[dict]) -> None:
    with path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import 480 public wireless headphone listings")
    parser.add_argument("--blob-json", type=Path, help="Use a locally downloaded GitHub API blob response")
    args = parser.parse_args()
    if RAW.exists() or SAMPLE.exists():
        raise FileExistsError("原始数据或 50 条样本已存在；脚本不会覆盖。")
    source = source_bytes(args.blob_json)
    rows = select_rows(source)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    write_csv_exclusive(RAW, rows)
    write_csv_exclusive(SAMPLE, rows[:50])
    log = {"event": "import", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
           "repository": REPO, "commit": COMMIT, "blob_sha": BLOB_SHA,
           "source_sha256": hashlib.sha256(source).hexdigest(),
           "raw_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
           "raw_rows": len(rows), "sample_rows": 50,
           "explicit_title_rows": sum(r["bluetooth_evidence"] == "explicit_title" for r in rows),
           "proxy_rows": sum(r["bluetooth_evidence"] == "wireless_flag_proxy" for r in rows)}
    (ROOT / "outputs" / "collection_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存 {len(rows)} 条原始记录和 50 条抽样记录；原始文件不会被覆盖。")


if __name__ == "__main__":
    main()

