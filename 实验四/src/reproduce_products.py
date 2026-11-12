"""Rebuild experiment-three clean_data.csv inside this isolated project."""

import base64
import csv
import hashlib
import io
import json
import urllib.request
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOB_SHA = "a652532a226278f4cba856efdcd97b2cf62cf2d7"
EXPECTED_CLEAN_SHA256 = "0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55"
URL = f"https://api.github.com/repos/Haseeb-U/ebay-headphones-market-dataset/git/blobs/{BLOB_SHA}"
RAW_FIELDS = ("listing_id", "title", "brand", "price", "currency", "rating",
              "reviews_count", "watchers_count", "scrape_timestamp", "wireless", "bluetooth_evidence")
CLEAN_FIELDS = ("listing_id", "title", "brand", "price_usd", "rating", "reviews_count",
                "watchers_count", "scrape_date", "bluetooth_evidence", "price_outlier")
BRAND_ALIASES = {"sony": "Sony", "jlab": "JLab", "jbl": "JBL",
                 "beats by dr. dre": "Beats", "beats": "Beats", "bose": "Bose",
                 "skullcandy": "Skullcandy", "shokz": "Shokz"}


def csv_export(rows: list[dict], fields: tuple[str, ...]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def quantile(values: list[Decimal], fraction: Decimal) -> Decimal:
    ordered = sorted(values)
    position = Decimal(len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def reproduce(blob_json: Path) -> tuple[bytes, bytes, dict]:
    blob = json.loads(blob_json.read_text(encoding="utf-8"))
    if blob.get("sha") != BLOB_SHA or blob.get("encoding") != "base64":
        raise ValueError("来源版本不匹配。")
    original = base64.b64decode(blob["content"])
    git_hash = hashlib.sha1(f"blob {len(original)}\0".encode() + original).hexdigest()
    if git_hash != BLOB_SHA:
        raise ValueError("来源 blob 校验失败。")
    source = csv.DictReader(io.StringIO(original.decode("utf-8-sig"), newline=""))
    raw = []
    for row in source:
        title = (row.get("title") or "").lower()
        explicit = "bluetooth" in title
        proxy = "wireless" in title and (row.get("wireless") or "").strip() == "1.0"
        if not (explicit or proxy):
            continue
        if not all((row.get(field) or "").strip() for field in
                   ("listing_id", "title", "brand", "price", "rating", "reviews_count", "scrape_timestamp")):
            continue
        selected = {field: (row.get(field) or "").strip() for field in RAW_FIELDS[:-1]}
        selected["bluetooth_evidence"] = "explicit_title" if explicit else "wireless_flag_proxy"
        raw.append(selected)
        if len(raw) == 480:
            break
    if len(raw) != 480:
        raise ValueError("无法重现 480 条抽取记录。")

    by_id = {}
    for row in raw:
        listing_id = row["listing_id"]
        current = by_id.get(listing_id)
        if current is None:
            by_id[listing_id] = row
        else:
            rank = (row["scrape_timestamp"], bool(row["watchers_count"]))
            old_rank = (current["scrape_timestamp"], bool(current["watchers_count"]))
            if rank > old_rank:
                by_id[listing_id] = row
    cleaned = []
    for row in by_id.values():
        price = Decimal(row["price"])
        rating = Decimal(row["rating"])
        reviews = int(Decimal(row["reviews_count"]))
        watchers = int(Decimal(row["watchers_count"])) if row["watchers_count"] else None
        brand = BRAND_ALIASES.get(row["brand"].casefold(), row["brand"])
        cleaned.append({"listing_id": row["listing_id"], "title": row["title"], "brand": brand,
                        "price_usd": f"{price:.2f}", "rating": f"{rating:.1f}",
                        "reviews_count": str(reviews), "watchers_count": "" if watchers is None else str(watchers),
                        "scrape_date": datetime.fromisoformat(row["scrape_timestamp"]).date().isoformat(),
                        "bluetooth_evidence": row["bluetooth_evidence"], "price_outlier": "false"})
    prices = [Decimal(row["price_usd"]) for row in cleaned]
    q1 = quantile(prices, Decimal("0.25"))
    q3 = quantile(prices, Decimal("0.75"))
    upper = q3 + Decimal(3) * (q3 - q1)
    for row in cleaned:
        if Decimal(row["price_usd"]) > upper:
            row["price_outlier"] = "true"
    cleaned.sort(key=lambda row: row["listing_id"])
    clean_bytes = csv_export(cleaned, CLEAN_FIELDS)
    actual = hashlib.sha256(clean_bytes).hexdigest()
    if actual != EXPECTED_CLEAN_SHA256:
        raise ValueError(f"复现文件哈希不一致：{actual}")
    details = {"source_blob_sha": BLOB_SHA, "source_sha256": hashlib.sha256(original).hexdigest(),
               "raw_rows": len(raw), "clean_rows": len(cleaned), "clean_sha256": actual,
               "expected_experiment3_sha256": EXPECTED_CLEAN_SHA256,
               "exact_match": True}
    return csv_export(raw, RAW_FIELDS), clean_bytes, details


def main() -> None:
    raw_target = ROOT / "data" / "raw" / "product_subset.csv"
    clean_target = ROOT / "data" / "processed" / "clean_data.csv"
    if raw_target.exists() or clean_target.exists():
        raise FileExistsError("目标文件已存在，不覆盖。")
    request = urllib.request.Request(URL, headers={"User-Agent": "marketing-experiment04"})
    with urllib.request.urlopen(request, timeout=120) as response:
        blob = response.read()
    temporary = ROOT / "outputs" / "product_blob_response.json"
    temporary.write_bytes(blob)
    try:
        raw, clean, details = reproduce(temporary)
    finally:
        temporary.unlink(missing_ok=True)
    raw_target.write_bytes(raw)
    clean_target.write_bytes(clean)
    (ROOT / "outputs" / "product_reproduction.json").write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    print("已在实验四内精确复现实验三 clean_data.csv；SHA-256 匹配。")


if __name__ == "__main__":
    main()

