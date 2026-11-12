"""Compute pain-derived content gaps from real review codes and listing titles.

The score is descriptive: user mention rate × uncovered title share. It does not
infer demand, sales, or complete rival advertising coverage.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

if __package__:
    from .brand_voice import validate_brief
else:
    from brand_voice import validate_brief

ROOT = Path(__file__).resolve().parents[1]
ENCODED = ROOT / "data" / "processed" / "encoded_reviews.json"
PRODUCTS = ROOT / "data" / "processed" / "clean_data.csv"
SELLING = ROOT / "data" / "processed" / "selling_points.csv"
SCORES = ROOT / "data" / "processed" / "scores.csv"
OUTPUTS = ROOT / "outputs"
FOCAL = "Skullcandy"

THEMES = {
    "device_failure": {"name": "设备可靠性", "pattern": r"durab|reliab|warrant|long.last"},
    "battery": {"name": "续航与充电", "pattern": r"battery|playtime|runtime|charg|\bhours?\b"},
    "connectivity": {"name": "连接稳定性", "pattern": r"bluetooth|wireless|pairing|connection"},
    "fit": {"name": "佩戴适配", "pattern": r"\bfit\b|comfort|ergonomic|secure|ear tips"},
    "price": {"name": "价格与价值", "pattern": r"value|afford|budget|sale|deal|discount"},
    "sound": {"name": "声音表现", "pattern": r"sound|audio|bass|hi.fi"},
    "noise_cancellation": {"name": "降噪体验", "pattern": r"noise.cancel|\banc\b"},
    "packaging": {"name": "包装状态", "pattern": r"packag|\bbox\b|unboxing"},
    "product_condition": {"name": "商品状态", "pattern": r"\bnew\b|refurb|condition"},
    "support": {"name": "售后支持", "pattern": r"support|warranty"},
    "delivery": {"name": "配送", "pattern": r"shipping|delivery"},
    "taste": {"name": "口味", "pattern": r"taste|flavor"},
}

BRIEF_TEMPLATES = {
    "device_failure": ("反馈单耳停用的耳机使用者", "用实测条件说明单耳寿命检查与保修边界。", "保修说明点击率=点击人数/内容曝光人数；基线待收集"),
    "battery": ("反馈充电或续航问题的耳机使用者", "在统一音量与模式条件下实测续航，并说明充电排查步骤。", "充电排查页点击率=点击人数/内容曝光人数；基线待收集"),
    "fit": ("反馈耳塞尺寸不合适的耳机使用者", "展示耳塞尺寸对照与试戴步骤，说明适配差异。", "尺寸指南使用率=指南访问人数/内容曝光人数；基线待收集"),
    "price": ("反馈价格与价值不符的耳机使用者", "用条件化对照解释价格、功能与保修范围。", "价格说明页点击率=点击人数/内容曝光人数；基线待收集"),
    "sound": ("反馈声音表现问题的耳机使用者", "用可复核条件展示声音对照与设置步骤。", "声音设置指南完成率=完整阅读人数/访问人数；基线待收集"),
    "noise_cancellation": ("反馈降噪不足的耳机使用者", "用实测条件说明降噪表现与适用场景。", "降噪说明页完成率=完整阅读人数/访问人数；基线待收集"),
}


class DataError(ValueError):
    pass


def load_inputs(encoded_path: Path = ENCODED, product_path: Path = PRODUCTS,
                selling_path: Path = SELLING, score_path: Path = SCORES) -> tuple[list[dict], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        payload = json.loads(encoded_path.read_text(encoding="utf-8"))
        reviews = payload["records"]
        products = pd.read_csv(product_path, dtype={"listing_id": str}, encoding="utf-8-sig")
        selling = pd.read_csv(selling_path, encoding="utf-8-sig")
        scores = pd.read_csv(score_path, encoding="utf-8-sig")
    except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
        raise DataError(f"输入无法读取：{exc}") from exc
    if not isinstance(reviews, list) or not reviews:
        raise DataError("评论编码 records 为空。")
    if not {"listing_id", "title", "brand"}.issubset(products.columns):
        raise DataError("商品列表缺少 listing_id、title 或 brand。")
    if not {"brand", "selling_point", "listing_count"}.issubset(selling.columns):
        raise DataError("竞品卖点表缺少字段。")
    if not {"competitor", "rank_status"}.issubset(scores.columns):
        raise DataError("竞品排名表缺少字段。")
    if products["listing_id"].isna().any() or products["listing_id"].duplicated().any():
        raise DataError("商品 ID 为空或重复。")
    ids = set()
    for review in reviews:
        if not isinstance(review, dict) or not all(key in review for key in ("review_id", "review_text", "pain_tags", "evidence")):
            raise DataError("评论编码字段不完整。")
        if review["review_id"] in ids:
            raise DataError("评论 ID 重复。")
        ids.add(review["review_id"])
        evidence = review["evidence"].get("pain_tags") if isinstance(review["evidence"], dict) else None
        if not isinstance(review["pain_tags"], list) or not isinstance(evidence, dict) or set(review["pain_tags"]) != set(evidence):
            raise DataError("评论标签与证据不一致。")
        if any(tag not in THEMES for tag in review["pain_tags"]):
            raise DataError("出现未知需求主题。")
        for quote in evidence.values():
            if not isinstance(quote, str) or quote not in review["review_text"]:
                raise DataError("评论证据不是同条原文子串。")
    return reviews, products, selling, scores


def calculate(reviews: list[dict], products: pd.DataFrame, selling: pd.DataFrame,
              scores: pd.DataFrame, focal: str = FOCAL, competitors: list[str] | None = None) -> dict:
    if competitors is None:
        competitors = scores.loc[scores["rank_status"].eq("ranked"), "competitor"].dropna().astype(str).tolist()
    competitors = list(dict.fromkeys(competitors))
    if not competitors or focal in competitors:
        raise DataError("必须选择至少一个非焦点竞品。")
    if any(brand not in set(products["brand"]) for brand in competitors):
        raise DataError("竞品品牌不在商品列表中。")
    competitor_products = products.loc[products["brand"].isin(competitors)].copy()
    # This source snapshot includes a Bluetooth USB dongle. A content study
    # about headphones excludes accessories without an earbud/headphone title.
    is_headphone = competitor_products["title"].str.contains(
        r"earbud|earphone|airpods|headphone|headset|over-ear|on-ear", case=False, regex=True, na=False)
    excluded = competitor_products.loc[~is_headphone, ["listing_id", "brand", "title"]].copy()
    competitor_products = competitor_products.loc[is_headphone].copy()
    if competitor_products.empty:
        raise DataError("竞品标题没有耳机商品。")
    checked_ids = competitor_products["listing_id"].astype(str).tolist()
    n_users = len(reviews)
    n_titles = len(competitor_products)
    matrix = []
    evidence_rows = []
    brand_rows = []
    for tag, spec in THEMES.items():
        user_rows = [row for row in reviews if tag in row["pain_tags"]]
        matched = competitor_products.loc[competitor_products["title"].str.contains(
            spec["pattern"], case=False, regex=True, na=False)]
        user_count = len(user_rows)
        title_count = len(matched)
        importance = user_count / n_users * 100
        coverage = title_count / n_titles * 100
        opportunity = importance * (1 - title_count / n_titles)
        status = "opportunity" if user_count >= 3 and coverage <= 25 and opportunity > 0 else (
            "pseudo_gap_low_user_interest" if user_count < 3 and coverage < 25 else "covered_or_low_gap")
        matrix.append({"theme": tag, "need_theme": spec["name"], "user_mentions": user_count,
                       "user_denominator": n_users, "user_sample_size": n_users,
                       "user_importance_percent": round(importance, 2),
                       "competitor_titles_covered": title_count, "competitor_title_denominator": n_titles,
                       "competitor_title_sample_size": n_titles,
                       "competitor_coverage_percent": round(coverage, 2),
                       "opportunity_score": round(opportunity, 2), "status": status})
        for row in user_rows:
            evidence_rows.append({"theme": tag, "evidence_type": "user_review",
                                  "source_id": row["review_id"], "brand": row.get("brand", ""),
                                  "exact_quote_or_title": row["evidence"]["pain_tags"][tag],
                                  "checked_title_count": n_titles})
        for row in matched.to_dict("records"):
            match = re.search(spec["pattern"], row["title"], re.I)
            evidence_rows.append({"theme": tag, "evidence_type": "competitor_title_match",
                                  "source_id": row["listing_id"], "brand": row["brand"],
                                  "exact_quote_or_title": match.group(0) if match else "",
                                  "checked_title_count": n_titles})
        # This explicit audit row makes zero coverage traceable to every title checked.
        evidence_rows.append({"theme": tag, "evidence_type": "competitor_title_audit",
                              "source_id": "|".join(checked_ids), "brand": "|".join(competitors),
                              "exact_quote_or_title": f"pattern={spec['pattern']}; matched={title_count}",
                              "checked_title_count": n_titles})
        for brand in competitors:
            subset = competitor_products.loc[competitor_products["brand"].eq(brand)]
            count = int(subset["title"].str.contains(spec["pattern"], case=False, regex=True, na=False).sum())
            brand_rows.append({"theme": tag, "competitor": brand, "covered_titles": count,
                               "checked_titles": len(subset),
                               "coverage_percent": round(count / len(subset) * 100, 2) if len(subset) else None})
    matrix_frame = pd.DataFrame(matrix).sort_values(["opportunity_score", "theme"], ascending=[False, True]).reset_index(drop=True)
    evidence_frame = pd.DataFrame(evidence_rows)
    brand_frame = pd.DataFrame(brand_rows)
    candidates = matrix_frame.loc[matrix_frame["status"].eq("opportunity")]
    briefs = []
    for row in candidates.to_dict("records"):
        tag = row["theme"]
        if tag not in BRIEF_TEMPLATES:
            continue
        audience, direction, metric = BRIEF_TEMPLATES[tag]
        evidence_ids = [r["review_id"] for r in reviews if tag in r["pain_tags"]]
        matched_ids = competitor_products.loc[competitor_products["title"].str.contains(
            THEMES[tag]["pattern"], case=False, regex=True, na=False), "listing_id"].astype(str).tolist()
        brief = {"theme": tag, "need_theme": THEMES[tag]["name"],
                 "target_audience": audience, "content_direction": direction,
                 "user_evidence_ids": evidence_ids[:5], "competitor_checked_listing_ids": checked_ids,
                 "competitor_matched_listing_ids": matched_ids,
                 "user_mentions": int(row["user_mentions"]), "user_denominator": n_users,
                 "competitor_titles_covered": int(row["competitor_titles_covered"]),
                 "competitor_title_denominator": n_titles,
                 "opportunity_score": float(row["opportunity_score"]),
                 "expected_metric": metric,
                 "claim_boundary": "仅作为内容试验方向；产品性能与用户需求仍需实测和更广样本验证。"}
        errors = validate_brief(brief)
        if errors:
            raise DataError(f"Brief {tag} 不符合 Brand Voice：{' '.join(errors)}")
        briefs.append(brief)
    if len(briefs) < 5:
        raise DataError(f"仅形成 {len(briefs)} 条合格 Brief，少于 5 条。")
    # Experiment-five ANC title counts are used as a source consistency check.
    anc_expected = selling.loc[selling["brand"].isin(competitors) & selling["selling_point"].eq("ANC mentioned in title"), "listing_count"].sum()
    anc_actual_before_exclusion = products.loc[products["brand"].isin(competitors), "title"].str.contains(
        r"noise.cancel|\banc\b", case=False, regex=True, na=False).sum()
    if int(anc_expected) != int(anc_actual_before_exclusion):
        raise DataError("实验五卖点表与商品标题的 ANC 计数不一致。")
    summary = {"version": "v0.6", "focal_brand": focal, "competitors": competitors,
               "review_sample_size": n_users, "competitor_title_sample_size": n_titles,
               "excluded_accessory_count": len(excluded),
               "opportunity_count": int(matrix_frame["status"].eq("opportunity").sum()),
               "brief_count": len(briefs), "coverage_scope": "competitor listing titles only",
               "selling_points_anc_count_verified": int(anc_expected),
               "pseudo_gap_example": "taste"}
    return {"theme_matrix": matrix_frame, "competitor_brand_coverage": brand_frame,
            "evidence_record": evidence_frame, "excluded_accessories": excluded,
            "briefs": briefs, "summary": summary}


def write_outputs(result: dict, output_dir: Path, paths: list[Path]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    result["theme_matrix"].to_csv(output_dir / "theme_matrix.csv", index=False, encoding="utf-8-sig")
    result["theme_matrix"].loc[result["theme_matrix"]["status"].eq("opportunity")].to_csv(
        output_dir / "opportunity_scores.csv", index=False, encoding="utf-8-sig")
    for name in ("competitor_brand_coverage", "evidence_record", "excluded_accessories"):
        result[name].to_csv(output_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    (output_dir / "strategy_briefs.json").write_text(json.dumps(result["briefs"], ensure_ascii=False, indent=2), encoding="utf-8")
    summary = dict(result["summary"])
    summary["source_sha256"] = {str(path.name): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    reviews, products, selling, scores = load_inputs()
    result = calculate(reviews, products, selling, scores)
    write_outputs(result, OUTPUTS, [ENCODED, PRODUCTS, SELLING, SCORES])
    print(f"已生成 {result['summary']['opportunity_count']} 个机会和 {len(result['briefs'])} 条策略 Brief。")


if __name__ == "__main__":
    main()

