"""Compute a reproducible, evidence-linked competition index with pandas.

No semantic labels are generated here. Review tags are inputs from experiment four.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from src.path_security import project_path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "data" / "processed" / "clean_data.csv"
REVIEWS = ROOT / "data" / "processed" / "encoded_reviews.json"
OUTPUTS = ROOT / "outputs"
DEFAULT_FOCAL = "Skullcandy"
ALLOWED_PAIN_TAGS = {"price", "taste", "delivery", "packaging", "battery", "fit",
                     "connectivity", "sound", "device_failure", "noise_cancellation",
                     "product_condition", "support"}
WEIGHTS = {"consumer_overlap": 0.30, "product_overlap": 0.25,
           "price_overlap": 0.20, "brand_heat": 0.25}
SCENARIOS = {
    "base": WEIGHTS,
    "consumer_plus_10pp": {"consumer_overlap": 0.40, "product_overlap": 0.20, "price_overlap": 0.15, "brand_heat": 0.25},
    "product_plus_15pp": {"consumer_overlap": 0.20, "product_overlap": 0.40, "price_overlap": 0.15, "brand_heat": 0.25},
    "price_plus_15pp": {"consumer_overlap": 0.20, "product_overlap": 0.20, "price_overlap": 0.35, "brand_heat": 0.25},
    "heat_plus_20pp": {"consumer_overlap": 0.20, "product_overlap": 0.20, "price_overlap": 0.15, "brand_heat": 0.45},
    "consumer_dominant_stress": {"consumer_overlap": 0.70, "product_overlap": 0.10, "price_overlap": 0.05, "brand_heat": 0.15},
}
EXPECTED_PRODUCT_SHA = "0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55"


class DataError(ValueError):
    pass


def _price_band(value: float) -> str:
    if value < 50:
        return "under_50"
    if value < 100:
        return "50_to_99"
    if value < 200:
        return "100_to_199"
    return "200_plus"


def _form_factor(title: str) -> str:
    lowered = title.casefold()
    if re.search(r"earbud|earphone|airpods|in-ear|\bbuds\b", lowered):
        return "earbuds"
    if re.search(r"headphone|headset|over-ear|on-ear", lowered):
        return "headphones"
    return "unspecified"


def _product_segment(title: str) -> str:
    anc_mentioned = bool(re.search(r"noise.cancel|\banc\b", title, re.I))
    return _form_factor(title) + ("_anc_mentioned" if anc_mentioned else "_anc_not_mentioned")


def _hist_overlap(left: pd.Series, right: pd.Series) -> float:
    lp = left.value_counts(normalize=True)
    rp = right.value_counts(normalize=True)
    return float(sum(min(lp.get(key, 0.0), rp.get(key, 0.0)) for key in set(lp.index) | set(rp.index)))


def _consumer_overlap(focal: list[dict], rival: list[dict]) -> tuple[float | None, list[str]]:
    tags = sorted({tag for record in focal + rival for tag in record["pain_tags"]})
    if not tags:
        return None, []
    left = {tag: sum(tag in record["pain_tags"] for record in focal) / len(focal) for tag in tags}
    right = {tag: sum(tag in record["pain_tags"] for record in rival) / len(rival) for tag in tags}
    denominator = sum(max(left[tag], right[tag]) for tag in tags)
    if denominator == 0:
        return None, []
    shared = [tag for tag in tags if left[tag] > 0 and right[tag] > 0]
    return sum(min(left[tag], right[tag]) for tag in tags) / denominator, shared


def _safe_ids(values: list[str], limit: int = 4) -> str:
    return "|".join(values[:limit])


def _metric_evidence(focal: str, rival: str, fp: pd.DataFrame, rp: pd.DataFrame,
                     fr: list[dict], rr: list[dict], shared_tags: list[str], metrics: dict) -> list[dict]:
    rows = []
    for metric in WEIGHTS:
        if metric == "consumer_overlap":
            tag = shared_tags[0] if shared_tags else "none"
            focal_ids = [r["review_id"] for r in fr if tag in r["pain_tags"]]
            rival_ids = [r["review_id"] for r in rr if tag in r["pain_tags"]]
            source = "encoded_reviews.json: pain_tags; review_id"
            detail = "shared_tag=" + tag + "; all tag frequencies used in weighted Jaccard"
        elif metric == "product_overlap":
            common = sorted(set(fp["product_segment"]) & set(rp["product_segment"]))
            segment = common[0] if common else "none"
            focal_ids = fp.loc[fp["product_segment"].eq(segment), "listing_id"].astype(str).tolist()
            rival_ids = rp.loc[rp["product_segment"].eq(segment), "listing_id"].astype(str).tolist()
            source = "clean_data.csv: title; listing_id"
            detail = "shared_segment=" + segment + "; full segment distributions used"
        elif metric == "price_overlap":
            common = sorted(set(fp["price_band"]) & set(rp["price_band"]))
            band = common[0] if common else "none"
            focal_ids = fp.loc[fp["price_band"].eq(band), "listing_id"].astype(str).tolist()
            rival_ids = rp.loc[rp["price_band"].eq(band), "listing_id"].astype(str).tolist()
            source = "clean_data.csv: price_usd; listing_id"
            detail = "shared_price_band=" + band + "; full band distributions used"
        else:
            focal_ids = []
            rival_ids = rp.sort_values("reviews_count", ascending=False)["listing_id"].astype(str).tolist()
            source = "clean_data.csv: reviews_count; listing_id"
            detail = "median review count per rival listing; relative to candidate brands"
        rows.append({"focal_brand": focal, "competitor": rival, "metric": metric,
                     "metric_score_0_100": None if metrics[metric] is None else round(metrics[metric], 4),
                     "source_fields": source, "focal_example_ids": _safe_ids(focal_ids),
                     "competitor_example_ids": _safe_ids(rival_ids), "detail": detail})
    return rows


def load_inputs(product_path: Path = PRODUCTS, review_path: Path = REVIEWS) -> tuple[pd.DataFrame, list[dict]]:
    product_path = project_path(product_path)
    review_path = project_path(review_path)
    try:
        products = pd.read_csv(product_path, dtype={"listing_id": str}, encoding="utf-8-sig")
    except (OSError, pd.errors.ParserError) as exc:
        raise DataError(f"商品 CSV 无法读取：{exc}") from exc
    required = {"listing_id", "title", "brand", "price_usd", "rating", "reviews_count", "scrape_date"}
    missing = sorted(required - set(products.columns))
    if missing:
        raise DataError("商品 CSV 缺少字段：" + "、".join(missing))
    if products.empty or products["listing_id"].isna().any() or products["listing_id"].duplicated().any():
        raise DataError("商品列表编号为空或重复。")
    if products["title"].isna().any() or products["title"].astype(str).str.strip().eq("").any():
        raise DataError("商品标题为空。")
    for field in ("price_usd", "rating", "reviews_count"):
        products[field] = pd.to_numeric(products[field], errors="coerce")
        if products[field].isna().any():
            raise DataError(f"商品字段 {field} 有无效数值。")
    if products["price_usd"].le(0).any() or (~products["rating"].between(0, 5)).any() or products["reviews_count"].lt(0).any():
        raise DataError("商品价格、评分或评论数超出允许范围。")
    if products["brand"].isna().any() or products["brand"].astype(str).str.strip().eq("").any():
        raise DataError("商品品牌为空。")
    try:
        data = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataError(f"评论编码 JSON 无法读取：{exc}") from exc
    reviews = data.get("records") if isinstance(data, dict) else None
    if not isinstance(reviews, list) or not reviews:
        raise DataError("评论编码缺少 records 数组。")
    ids = []
    for review in reviews:
        if not isinstance(review, dict) or not all(key in review for key in ("review_id", "review_text", "brand", "pain_tags", "evidence", "sentiment")):
            raise DataError("评论编码字段不完整。")
        if not isinstance(review["review_id"], str) or not review["review_id"] or not isinstance(review["review_text"], str) or not review["review_text"] or not isinstance(review["brand"], str) or not review["brand"]:
            raise DataError("评论 ID、正文或品牌为空。")
        if not isinstance(review["evidence"], dict) or not isinstance(review["pain_tags"], list) or not isinstance(review["evidence"].get("pain_tags"), dict):
            raise DataError("评论痛点标签或证据格式错误。")
        if len(review["pain_tags"]) != len(set(review["pain_tags"])) or any(tag not in ALLOWED_PAIN_TAGS for tag in review["pain_tags"]):
            raise DataError("评论痛点标签重复或不在允许值内。")
        if set(review["pain_tags"]) != set(review["evidence"]["pain_tags"]):
            raise DataError("评论痛点与证据标签不一致。")
        for quote in review["evidence"]["pain_tags"].values():
            if not isinstance(quote, str) or quote not in review["review_text"]:
                raise DataError("评论证据不是对应原文子串。")
        ids.append(review["review_id"])
    if len(ids) != len(set(ids)):
        raise DataError("评论 ID 重复。")
    products["product_segment"] = products["title"].map(_product_segment)
    products["price_band"] = products["price_usd"].map(_price_band)
    products["anc_mentioned"] = products["title"].str.contains(r"noise.cancel|\banc\b", case=False, regex=True)
    return products, reviews


def calculate(products: pd.DataFrame, reviews: list[dict], focal: str = DEFAULT_FOCAL,
              weights: dict[str, float] | None = None) -> dict:
    weights = dict(WEIGHTS if weights is None else weights)
    if set(weights) != set(WEIGHTS) or any(value < 0 for value in weights.values()) or abs(sum(weights.values()) - 1.0) > 1e-9:
        raise DataError("权重必须包含四项非负指标且合计为 100%。")
    review_brands = {r["brand"] for r in reviews}
    product_brands = set(products["brand"])
    candidates = sorted(review_brands & product_brands)
    if focal not in candidates:
        raise DataError(f"焦点品牌 {focal} 必须同时存在于商品与评论数据。")
    fp = products.loc[products["brand"].eq(focal)]
    fr = [r for r in reviews if r["brand"] == focal]
    median_counts = products.loc[products["brand"].isin(candidates)].groupby("brand")["reviews_count"].median()
    heat_rank = median_counts.rank(method="average", pct=True).mul(100)
    scores = []
    evidence = []
    for rival in candidates:
        if rival == focal:
            continue
        rp = products.loc[products["brand"].eq(rival)]
        rr = [r for r in reviews if r["brand"] == rival]
        consumer, shared = _consumer_overlap(fr, rr)
        metrics = {
            "consumer_overlap": None if consumer is None else consumer * 100,
            "product_overlap": _hist_overlap(fp["product_segment"], rp["product_segment"]) * 100,
            "price_overlap": _hist_overlap(fp["price_band"], rp["price_band"]) * 100,
            "brand_heat": float(heat_rank[rival]),
        }
        eligible = len(rr) >= 3 and len(fr) >= 3 and consumer is not None
        score = sum(metrics[key] * weights[key] for key in WEIGHTS) if eligible else None
        scores.append({"focal_brand": focal, "competitor": rival,
                       "consumer_overlap": metrics["consumer_overlap"],
                       "product_overlap": metrics["product_overlap"],
                       "price_overlap": metrics["price_overlap"],
                       "brand_heat": metrics["brand_heat"],
                       "threat_index": score, "rank_status": "ranked" if eligible else "insufficient_review_sample",
                       "review_sample_size": len(rr), "product_listing_count": len(rp),
                       "focal_review_sample_size": len(fr), "focal_product_listing_count": len(fp),
                       "product_sample_warning": len(rp) < 3,
                       "shared_pain_tags": "|".join(shared)})
        evidence.extend(_metric_evidence(focal, rival, fp, rp, fr, rr, shared, metrics))
    scores_frame = pd.DataFrame(scores)
    scores_frame["threat_index"] = pd.to_numeric(scores_frame["threat_index"], errors="coerce").round(4)
    scores_frame[[*WEIGHTS]] = scores_frame[[*WEIGHTS]].apply(pd.to_numeric, errors="coerce").round(4)
    scores_frame["_ranked_first"] = scores_frame["rank_status"].eq("ranked")
    scores_frame = scores_frame.sort_values(["_ranked_first", "threat_index", "competitor"],
                                            ascending=[False, False, True]).drop(columns="_ranked_first").reset_index(drop=True)
    scores_frame["rank"] = pd.NA
    mask = scores_frame["rank_status"].eq("ranked")
    scores_frame.loc[mask, "rank"] = range(1, int(mask.sum()) + 1)

    structure = products.groupby(["brand", "product_segment"], as_index=False).agg(
        listing_count=("listing_id", "nunique"), average_rating=("rating", "mean"))
    structure["average_rating"] = structure["average_rating"].round(2)
    prices = products.groupby(["brand", "price_band"], as_index=False).agg(
        listing_count=("listing_id", "nunique"), average_price_usd=("price_usd", "mean"))
    prices["average_price_usd"] = prices["average_price_usd"].round(2)
    ratings = products.groupby("brand", as_index=False).agg(
        listing_count=("listing_id", "nunique"), average_listing_rating=("rating", "mean"),
        median_reviews_count=("reviews_count", "median"))
    ratings[["average_listing_rating", "median_reviews_count"]] = ratings[
        ["average_listing_rating", "median_reviews_count"]].round(2)
    selling = products.groupby(["brand", "anc_mentioned"], as_index=False).agg(
        listing_count=("listing_id", "nunique"))
    selling["selling_point"] = selling["anc_mentioned"].map({True: "ANC mentioned in title", False: "ANC not mentioned"})
    selling = selling.drop(columns="anc_mentioned")
    gap = products.groupby(["product_segment", "price_band"], as_index=False).agg(
        listing_count=("listing_id", "nunique"),
        example_listing_ids=("listing_id", lambda ids: "|".join(sorted(ids.astype(str).tolist())[:3])))
    gap["share_of_all_listings_percent"] = gap["listing_count"].div(len(products)).mul(100).round(2)
    gap = gap.sort_values(["listing_count", "product_segment", "price_band"]).reset_index(drop=True)
    summary = {"version": "v0.5", "focal_brand": focal, "weights": weights,
               "weights_sum": sum(weights.values()), "product_rows": len(products),
               "review_rows": len(reviews), "focal_review_sample_size": len(fr),
               "candidate_brands": candidates, "ranked_competitors": int(mask.sum()),
               "consumer_overlap_is_pain_profile_proxy": True,
               "no_shared_product_or_consumer_identifier": True,
               "minimum_rival_reviews_for_rank": 3,
               "product_sample_warning_below": 3}
    return {"scores": scores_frame, "evidence": pd.DataFrame(evidence),
            "product_structure": structure, "price_bands": prices,
            "brand_ratings": ratings, "selling_points": selling,
            "market_gap_segments": gap, "summary": summary}


def sensitivity(products: pd.DataFrame, reviews: list[dict], focal: str) -> pd.DataFrame:
    rows = []
    for name, weights in SCENARIOS.items():
        result = calculate(products, reviews, focal, weights)["scores"]
        for row in result.to_dict("records"):
            rows.append({"scenario": name, "focal_brand": focal, "competitor": row["competitor"],
                         "rank_status": row["rank_status"], "rank": row["rank"],
                         "threat_index": row["threat_index"], **{f"weight_{key}": value for key, value in weights.items()}})
    return pd.DataFrame(rows)


def write_outputs(result: dict, sensitivity_frame: pd.DataFrame, output_dir: Path,
                  product_path: Path, review_path: Path) -> None:
    output_dir = project_path(output_dir)
    product_path = project_path(product_path)
    review_path = project_path(review_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in result.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(output_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    sensitivity_frame.to_csv(output_dir / "sensitivity.csv", index=False, encoding="utf-8-sig")
    summary = dict(result["summary"])
    summary["product_sha256"] = hashlib.sha256(product_path.read_bytes()).hexdigest()
    summary["encoded_review_sha256"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate brand competition index")
    parser.add_argument("--focal", default=DEFAULT_FOCAL, help="Brand present in both data sources")
    args = parser.parse_args()
    products, reviews = load_inputs()
    result = calculate(products, reviews, args.focal)
    write_outputs(result, sensitivity(products, reviews, args.focal), OUTPUTS, PRODUCTS, REVIEWS)
    print(f"竞争指标已生成：焦点品牌 {args.focal}，可排名竞品 {result['summary']['ranked_competitors']} 个。")


if __name__ == "__main__":
    main()

