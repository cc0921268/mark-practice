"""Parse AI-authored codes and compute all statistics with pandas.

This module does not assign semantic labels. It rejects unsupported labels or
quotes and only counts, groups, sorts, and formats the supplied annotations.
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.path_security import project_path, project_source

ROOT = Path(__file__).resolve().parents[1]
PAIN_TAGS = ("price", "taste", "delivery", "packaging", "battery", "fit",
             "connectivity", "sound", "device_failure", "noise_cancellation",
             "product_condition", "support")
SENTIMENTS = ("positive", "negative", "mixed", "neutral", "unknown")
SCENARIOS = ("workout", "commute", "travel", "outdoor", "home", "office", "unknown")
BARRIERS = ("price", "trust", "delivery", "specification", "unknown")
REVIEW_FIELDS = ("review_id", "product_name", "brand", "rating", "review_text", "review_date", "helpful_count")
PRODUCT_FIELDS = ("listing_id", "title", "brand", "price_usd", "rating", "reviews_count", "watchers_count", "scrape_date")


class InputError(ValueError):
    pass


def _quote(value: str, text: str, label: str) -> None:
    if not isinstance(value, str) or not value or value not in text:
        raise InputError(f"{label} 的证据不是原评论子串。")


def load_reviews(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(project_source(path), dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [field for field in REVIEW_FIELDS if field not in frame.columns]
    if missing:
        raise InputError("评论 CSV 缺少字段：" + "、".join(missing))
    frame = frame.loc[:, REVIEW_FIELDS].copy()
    frame["review_id"] = frame["review_id"].str.strip()
    frame["review_text"] = frame["review_text"].str.strip()
    if frame.empty or frame["review_id"].eq("").any() or frame["review_text"].eq("").any():
        raise InputError("评论 ID 或正文为空。")
    if frame["review_id"].duplicated().any():
        raise InputError("评论 ID 重复。")
    rating = pd.to_numeric(frame["rating"], errors="coerce")
    if rating.isna().any() or (~rating.between(0, 5)).any():
        raise InputError("评论评分无效。")
    frame["rating"] = rating
    return frame


def encode(reviews: pd.DataFrame, annotations: list[dict]) -> list[dict]:
    if not isinstance(annotations, list):
        raise InputError("语义编码必须为 JSON 数组。")
    ids = [entry.get("review_id") for entry in annotations if isinstance(entry, dict)]
    if len(ids) != len(annotations) or len(ids) != len(set(ids)):
        raise InputError("语义编码的评论 ID 缺失或重复。")
    by_id = {entry["review_id"]: entry for entry in annotations}
    source_ids = set(reviews["review_id"])
    if set(by_id) != source_ids:
        raise InputError("语义编码与原评论 ID 不完全一致。")
    encoded = []
    for row in reviews.to_dict("records"):
        review_id = row["review_id"]
        text = row["review_text"]
        entry = by_id[review_id]
        sentiment = entry.get("sentiment", "unknown")
        if sentiment not in SENTIMENTS:
            raise InputError(f"{review_id} 情绪标签无效。")
        sentiment_quotes = entry.get("sentiment_evidence", [])
        if not isinstance(sentiment_quotes, list) or (sentiment != "unknown" and not sentiment_quotes):
            raise InputError(f"{review_id} 情绪证据缺失。")
        for quote in sentiment_quotes:
            _quote(quote, text, review_id + " 情绪")
        pain_map = entry.get("pain_tags", {})
        if not isinstance(pain_map, dict) or any(tag not in PAIN_TAGS for tag in pain_map):
            raise InputError(f"{review_id} 痛点标签无效。")
        for tag, quote in pain_map.items():
            _quote(quote, text, review_id + " " + tag)
        scenario = entry.get("scenario", "unknown")
        if scenario not in SCENARIOS:
            raise InputError(f"{review_id} 场景标签无效。")
        scenario_quote = entry.get("scenario_evidence")
        if scenario == "unknown":
            if scenario_quote is not None:
                raise InputError(f"{review_id} 未知场景不应附证据。")
        else:
            _quote(scenario_quote, text, review_id + " 场景")
        barrier = entry.get("purchase_barrier", "unknown")
        if barrier not in BARRIERS:
            raise InputError(f"{review_id} 购买障碍标签无效。")
        barrier_quote = entry.get("purchase_barrier_evidence")
        if barrier == "unknown":
            if barrier_quote is not None:
                raise InputError(f"{review_id} 未知购买障碍不应附证据。")
        else:
            _quote(barrier_quote, text, review_id + " 购买障碍")
        first_tag = next(iter(pain_map), "unknown")
        evidence = {"sentiment": sentiment_quotes or None, "need": None,
                    "pain_point": pain_map[first_tag] if first_tag != "unknown" else None,
                    "scenario": scenario_quote, "purchase_barrier": barrier_quote,
                    "pain_tags": pain_map}
        encoded.append({"review_id": review_id, "review_text": text, "brand": row["brand"],
                        "product_name": row["product_name"],
                        "review_date": row["review_date"] or None,
                        "rating": float(row["rating"]), "sentiment": sentiment,
                        "need": "unknown", "pain_point": first_tag, "scenario": scenario,
                        "purchase_barrier": barrier, "pain_tags": list(pain_map),
                        "evidence": evidence,
                        "confidence": 0.95 if sentiment_quotes or pain_map or scenario_quote or barrier_quote else 0.0})
    return encoded


def statistics(records: list[dict], products: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    if not records:
        raise InputError("没有编码记录。")
    missing = [field for field in PRODUCT_FIELDS if field not in products.columns]
    if missing:
        raise InputError("商品清洗数据缺少字段：" + "、".join(missing))
    n = len(records)
    coded = pd.DataFrame(records)
    pairs = pd.DataFrame([
        {"review_id": record["review_id"], "brand": record["brand"],
         "pain_tag": tag, "evidence_quote": quote}
        for record in records for tag, quote in record["evidence"]["pain_tags"].items()
    ], columns=["review_id", "brand", "pain_tag", "evidence_quote"])
    pain_rows = []
    for tag in PAIN_TAGS:
        count = int(pairs["pain_tag"].eq(tag).sum())
        pain_rows.append({"pain_tag": tag, "count": count, "denominator": n,
                          "sample_size": n, "percent": round(count / n * 100, 2)})
    pain = pd.DataFrame(pain_rows).sort_values(["count", "pain_tag"], ascending=[False, True]).reset_index(drop=True)
    emotion = pd.DataFrame([{"sentiment": value, "count": int(coded["sentiment"].eq(value).sum()),
                             "denominator": n, "sample_size": n,
                             "percent": round(float(coded["sentiment"].eq(value).sum()) / n * 100, 2)}
                            for value in SENTIMENTS])
    brand_rows = []
    for brand, group in coded.groupby("brand", sort=True):
        count = len(group)
        negative = int(group["sentiment"].eq("negative").sum())
        brand_rows.append({"brand": brand, "review_count": count, "denominator": count,
                           "sample_size": count, "negative_count": negative,
                           "negative_percent": round(negative / count * 100, 2)})
    brand_emotion = pd.DataFrame(brand_rows)
    brand_pain_rows = []
    for brand, group in coded.groupby("brand", sort=True):
        denom = len(group)
        for tag in PAIN_TAGS:
            count = int(((pairs["brand"] == brand) & (pairs["pain_tag"] == tag)).sum())
            brand_pain_rows.append({"brand": brand, "pain_tag": tag, "count": count,
                                    "denominator": denom, "sample_size": denom,
                                    "percent": round(count / denom * 100, 2)})
    brand_pain = pd.DataFrame(brand_pain_rows)
    product = products.copy()
    product["price_usd"] = pd.to_numeric(product["price_usd"], errors="raise")
    product["rating"] = pd.to_numeric(product["rating"], errors="raise")
    product_brand = product.groupby("brand", as_index=False).agg(
        listing_count=("listing_id", "nunique"), average_list_price_usd=("price_usd", "mean"),
        average_listing_rating=("rating", "mean"))
    product_brand[["average_list_price_usd", "average_listing_rating"]] = product_brand[
        ["average_list_price_usd", "average_listing_rating"]].round(2)
    brand_comparison = brand_emotion.merge(product_brand, on="brand", how="left")
    product_time = product.groupby(["scrape_date", "brand"], as_index=False).agg(
        listing_count=("listing_id", "nunique"), average_list_price_usd=("price_usd", "mean"))
    product_time["average_list_price_usd"] = product_time["average_list_price_usd"].round(2)
    review_time_available = int(coded["review_date"].notna().sum())
    summary = {"version": "v0.4", "review_sample_size": n, "pain_denominator": n,
               "sentiment_denominator": n, "product_listing_count": len(product),
               "review_dates_available": review_time_available,
               "review_time_comparison": "unavailable" if review_time_available == 0 else "available",
               "pain_is_multi_label": True,
               "sample_is_targeted": True,
               "product_join_level": "brand_only_no_product_match"}
    return {"pain_ranking": pain, "sentiment_distribution": emotion,
            "brand_sentiment": brand_emotion, "brand_pain": brand_pain,
            "brand_comparison": brand_comparison, "product_snapshot_by_date": product_time,
            "evidence_index": pairs, "summary": summary}


def run(review_path: Path, annotation_path: Path, product_path: Path, output_dir: Path,
        clean_review_path: Path | None = None) -> dict:
    review_path = project_path(review_path)
    annotation_path = project_path(annotation_path)
    product_path = project_path(product_path)
    output_dir = project_path(output_dir)
    if clean_review_path is not None:
        clean_review_path = project_path(clean_review_path)
    reviews = load_reviews(review_path)
    annotations = json.loads(annotation_path.read_text(encoding="utf-8"))
    records = encode(reviews, annotations)
    products = pd.read_csv(product_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    stats = statistics(records, products)
    output_dir.mkdir(parents=True, exist_ok=True)
    if clean_review_path is not None:
        clean_review_path.parent.mkdir(parents=True, exist_ok=True)
        reviews.to_csv(clean_review_path, index=False, encoding="utf-8-sig")
    (output_dir / "encoded_reviews.json").write_text(
        json.dumps({"version": "v0.4", "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, frame in stats.items():
        if isinstance(frame, pd.DataFrame):
            frame.to_csv(output_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    summary = stats["summary"]
    summary["product_clean_sha256"] = hashlib.sha256(product_path.read_bytes()).hexdigest()
    summary["review_raw_sha256"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run(ROOT / "data" / "raw" / "reviews.csv",
                  ROOT / "data" / "processed" / "semantic_annotations.json",
                  ROOT / "data" / "processed" / "clean_data.csv",
                  ROOT / "outputs", ROOT / "data" / "processed" / "clean_reviews.csv")
    print(f"已由 pandas 统计 {summary['review_sample_size']} 条评论；分母与样本量已写入统计表。")


if __name__ == "__main__":
    main()

