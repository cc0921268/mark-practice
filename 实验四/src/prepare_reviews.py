"""Import a fixed, de-identified set of real earbud review texts."""

import argparse
import base64
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOB_SHA = "691f1f4651237049622435cdafd0f6de659dfab6"
SOURCE_SHA256 = "40c1c3885bb4e8f979e9ea1971f216a0ab6255c825cd95141ec81324ccedd3c7"
URL = f"https://api.github.com/repos/vfabuluje/beats-sentiment-analysis/git/blobs/{BLOB_SHA}"
IDS = (
    "RZ80S0WTLE5XV", "R235GNB2VHHLYC", "RHM04YLY2VYYR", "R1ATK4EOO6JDDH",
    "R15KN6XHFIEM00", "R26HEHTAA675XL", "R3LE7R8KC2FNBN", "R2XHEXEGVII1Y7",
    "R2ZIFDC71LMZTC", "R14S44XNYWAJ6S", "R291XLOCLTAGYX", "R3I5STGPGGKF8T",
    "RPNH0JRGVT2TA", "R3KWX129FATHZ5", "R16Y3N21ZBO7M9", "R3GHP7Y6NQQLW",
    "R3KSIVBNARMAB", "R2DG530TEWR0LU", "R1KOT9VQZRR9DP", "R1NZFMP5E3V7DO",
    "R33SEAQBU28DVP", "R3IJ6RANP5Z9KV", "R2789X65707AWW", "R3I10YETW6G46D",
    "R16JMJTVP2HUHC", "R3URZ9ZP4QCFJG", "R2PX0Z7BTN5ZLC", "R1WZ8PIXJM9AKI",
    "R2WOI29CCIOVO0", "R2TFU4XZKPCZWB",
)
FIELDS = ("review_id", "product_name", "brand", "rating", "review_text", "review_date", "helpful_count")


def brand_for(product_name: str) -> str:
    if product_name.startswith("Soundcore"):
        return "Anker"
    return product_name.split()[0]


def source_bytes(path: Path | None) -> bytes:
    if path is None:
        request = urllib.request.Request(URL, headers={"User-Agent": "marketing-experiment04"})
        with urllib.request.urlopen(request, timeout=60) as response:
            blob = json.load(response)
        if blob.get("sha") != BLOB_SHA or blob.get("encoding") != "base64":
            raise ValueError("评论来源版本不匹配。")
        source = base64.b64decode(blob["content"])
    else:
        source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("评论来源 SHA-256 不匹配。")
    return source


def prepare(source: bytes) -> tuple[list[dict], dict]:
    rows = csv.DictReader(io.StringIO(source.decode("utf-8-sig"), newline=""))
    by_id = {}
    for row in rows:
        if row["review_id"] in IDS and row["review_id"] not in by_id:
            by_id[row["review_id"]] = row
    missing = [review_id for review_id in IDS if review_id not in by_id]
    if missing:
        raise ValueError("来源缺少预定评论 ID：" + ", ".join(missing))
    clean = []
    for review_id in IDS:
        row = by_id[review_id]
        content = (row.get("content") or "").strip()
        if not content:
            raise ValueError(f"评论 {review_id} 正文为空。")
        product_name = (row.get("product_name") or "").strip()
        clean.append({"review_id": review_id, "product_name": product_name,
                      "brand": brand_for(product_name), "rating": (row.get("rating") or "").strip(),
                      "review_text": content, "review_date": (row.get("timestamp") or "").strip(),
                      "helpful_count": (row.get("helpful_count") or "").strip()})
    details = {"source_blob_sha": BLOB_SHA, "source_sha256": SOURCE_SHA256,
               "selected_rows": len(clean), "review_date_nonempty": sum(bool(row["review_date"]) for row in clean),
               "personal_columns_excluded": ["author", "profile_id"],
               "selection": "fixed review IDs; intentionally includes complaints and controls"}
    return clean, details


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="Existing source CSV within this project")
    args = parser.parse_args()
    target = ROOT / "data" / "raw" / "reviews.csv"
    if target.exists():
        raise FileExistsError("去标识化原始评论已存在，禁止覆盖。")
    rows, details = prepare(source_bytes(args.source))
    with target.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    details["sanitized_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    (ROOT / "outputs" / "review_import.json").write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保留 {len(rows)} 条真实评论，作者和资料编号未导入。")


if __name__ == "__main__":
    main()

