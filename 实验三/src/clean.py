"""Repeatable cleaning of the curated public headphone listing CSV."""

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "raw_data.csv"
CLEAN = ROOT / "data" / "processed" / "clean_data.csv"
RAW_FIELDS = ("listing_id", "title", "brand", "price", "currency", "rating",
              "reviews_count", "watchers_count", "scrape_timestamp", "wireless", "bluetooth_evidence")
CLEAN_FIELDS = ("listing_id", "title", "brand", "price_usd", "rating", "reviews_count",
                "watchers_count", "scrape_date", "bluetooth_evidence", "price_outlier")
ANALYTIC_FIELDS = CLEAN_FIELDS[:8]
BRAND_ALIASES = {"sony": "Sony", "jlab": "JLab", "jbl": "JBL",
                 "beats by dr. dre": "Beats", "beats": "Beats", "bose": "Bose",
                 "skullcandy": "Skullcandy", "shokz": "Shokz"}


class CleanError(ValueError):
    pass


def _decimal(value: str) -> Decimal | None:
    try:
        number = Decimal(value.strip())
        return number if number.is_finite() else None
    except (InvalidOperation, AttributeError):
        return None


def _integer(value: str) -> int | None:
    number = _decimal(value)
    if number is None or number < 0 or number != number.to_integral_value():
        return None
    return int(number)


def _quantile(values: list[Decimal], fraction: Decimal) -> Decimal:
    ordered = sorted(values)
    position = Decimal(len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def clean_bytes(raw: bytes) -> tuple[list[dict], dict, dict]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CleanError("CSV 编码错误：请使用 UTF-8。") from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        missing = [field for field in RAW_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise CleanError("CSV 缺少必需字段：" + "、".join(missing) + "。")
        input_rows = list(reader)
    except csv.Error as exc:
        raise CleanError(f"CSV 格式错误：{exc}") from exc
    if not input_rows:
        raise CleanError("CSV 没有数据行。")
    if len(input_rows) > 100000:
        raise CleanError("CSV 超过 100000 行，请拆分。")

    counts = {"duplicate_removed": 0, "invalid_price_removed": 0,
              "invalid_rating_removed": 0, "invalid_core_removed": 0,
              "invalid_date_removed": 0, "non_usd_removed": 0,
              "brand_alias_modified": 0, "watchers_invalid_to_blank": 0,
              "wireless_inferred_from_title": 0, "price_outlier_flagged": 0}
    by_id = {}
    for row in input_rows:
        if None in row:
            counts["invalid_core_removed"] += 1
            continue
        listing_id = (row.get("listing_id") or "").strip()
        if not listing_id:
            counts["invalid_core_removed"] += 1
            continue
        current = by_id.get(listing_id)
        if current is None:
            by_id[listing_id] = row
        else:
            counts["duplicate_removed"] += 1
            candidate_rank = ((row.get("scrape_timestamp") or ""), bool((row.get("watchers_count") or "").strip()))
            current_rank = ((current.get("scrape_timestamp") or ""), bool((current.get("watchers_count") or "").strip()))
            if candidate_rank > current_rank:
                by_id[listing_id] = row

    cleaned = []
    for row in by_id.values():
        title = (row.get("title") or "").strip()
        brand = (row.get("brand") or "").strip()
        evidence = (row.get("bluetooth_evidence") or "").strip()
        if not title or not brand or evidence not in ("explicit_title", "wireless_flag_proxy"):
            counts["invalid_core_removed"] += 1
            continue
        if (row.get("currency") or "").strip().upper() != "USD":
            counts["non_usd_removed"] += 1
            continue
        price = _decimal(row.get("price") or "")
        if price is None or price <= 0:
            counts["invalid_price_removed"] += 1
            continue
        rating = _decimal(row.get("rating") or "")
        if rating is None or not (Decimal(0) <= rating <= Decimal(5)):
            counts["invalid_rating_removed"] += 1
            continue
        reviews = _integer(row.get("reviews_count") or "")
        if reviews is None:
            counts["invalid_core_removed"] += 1
            continue
        try:
            date = datetime.fromisoformat((row.get("scrape_timestamp") or "").strip()).date().isoformat()
        except ValueError:
            counts["invalid_date_removed"] += 1
            continue
        watchers_text = (row.get("watchers_count") or "").strip()
        watchers = _integer(watchers_text) if watchers_text else None
        if watchers_text and watchers is None:
            counts["watchers_invalid_to_blank"] += 1
        normalized_brand = BRAND_ALIASES.get(brand.casefold(), brand)
        if normalized_brand != brand:
            counts["brand_alias_modified"] += 1
        if evidence == "explicit_title" and not (row.get("wireless") or "").strip():
            counts["wireless_inferred_from_title"] += 1
        cleaned.append({"listing_id": (row.get("listing_id") or "").strip(),
                        "title": title, "brand": normalized_brand,
                        "price_usd": f"{price:.2f}", "rating": f"{rating:.1f}",
                        "reviews_count": str(reviews),
                        "watchers_count": "" if watchers is None else str(watchers),
                        "scrape_date": date, "bluetooth_evidence": evidence,
                        "price_outlier": "false"})
    if not cleaned:
        raise CleanError("清洗后没有有效记录。")
    prices = [Decimal(row["price_usd"]) for row in cleaned]
    q1 = _quantile(prices, Decimal("0.25"))
    q3 = _quantile(prices, Decimal("0.75"))
    upper = q3 + Decimal(3) * (q3 - q1)
    for row in cleaned:
        if Decimal(row["price_usd"]) > upper:
            row["price_outlier"] = "true"
            counts["price_outlier_flagged"] += 1
    cleaned.sort(key=lambda row: row["listing_id"])
    completeness = {field: round(sum(bool(row[field]) for row in cleaned) / len(cleaned), 4)
                    for field in ANALYTIC_FIELDS}
    overall = round(sum(bool(row[field]) for row in cleaned for field in ANALYTIC_FIELDS)
                    / (len(cleaned) * len(ANALYTIC_FIELDS)), 4)
    quality = {"version": "v0.3", "raw_rows": len(input_rows), "clean_rows": len(cleaned),
               "unique_brands": len({row["brand"] for row in cleaned}),
               "analytic_field_completeness": overall,
               "field_completeness": completeness,
               "price_usd_min": str(min(prices)), "price_usd_max": str(max(prices)),
               "price_outlier_upper_usd": f"{upper:.2f}",
               "explicit_title_rows": sum(row["bluetooth_evidence"] == "explicit_title" for row in cleaned),
               "wireless_proxy_rows": sum(row["bluetooth_evidence"] == "wireless_flag_proxy" for row in cleaned),
               "review_text_available": False}
    log = {"rules": counts, "raw_rows": len(input_rows), "clean_rows": len(cleaned),
           "dedup_rule": "listing_id; latest scrape_timestamp, then nonblank watchers_count, then first row",
           "outlier_rule": "price > Q3 + 3*IQR; flag and retain"}
    return cleaned, quality, log


def csv_bytes(rows: list[dict]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CLEAN_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def main() -> None:
    raw = RAW.read_bytes()
    collection_log = json.loads((ROOT / "outputs" / "collection_log.json").read_text(encoding="utf-8"))
    raw_hash = hashlib.sha256(raw).hexdigest()
    if raw_hash != collection_log["raw_sha256"]:
        raise CleanError("原始文件哈希与采集记录不一致，停止清洗。")
    rows, quality, log = clean_bytes(raw)
    result = csv_bytes(rows)
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    temporary = CLEAN.with_suffix(".tmp")
    temporary.write_bytes(result)
    temporary.replace(CLEAN)
    log.update({"version": "v0.3", "run_time_utc": datetime.now(timezone.utc).isoformat(),
                "raw_sha256": raw_hash, "clean_sha256": hashlib.sha256(result).hexdigest(),
                "raw_file": str(RAW.relative_to(ROOT)), "clean_file": str(CLEAN.relative_to(ROOT))})
    (ROOT / "outputs" / "cleaning_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "outputs" / "quality_statistics.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"原始 {len(raw.splitlines()) - 1} 行，清洗后 {len(rows)} 行；原始文件未修改。")


if __name__ == "__main__":
    main()

