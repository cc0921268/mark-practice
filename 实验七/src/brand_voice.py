"""Callable quality checks for the fictional ClearWave course brand voice."""

import re

BRAND_NAME = "清波 ClearWave"
BANNED = ("绝对", "永久", "零故障", "100%", "行业第一", "彻底解决", "永不掉线", "包治", "保证有效")
PREFERRED = ("实测", "对照", "条件", "步骤", "说明", "适配")
METRIC_TERMS = ("/", "分母", "样本量")


def validate_text(text: str) -> list[str]:
    errors = []
    if not isinstance(text, str) or not text.strip():
        return ["内容方向为空。"]
    for word in BANNED:
        if word.casefold() in text.casefold():
            errors.append(f"含禁用词：{word}。")
    if not any(word in text for word in PREFERRED):
        errors.append("缺少可验证的表达词：实测、对照、条件、步骤、说明或适配。")
    sentences = [sentence.strip() for sentence in re.split(r"[。！？!?]", text) if sentence.strip()]
    if any(len(sentence) > 55 for sentence in sentences):
        errors.append("单句超过 55 个字符，应拆分。")
    return errors


def validate_brief(brief: dict) -> list[str]:
    required = ("theme", "target_audience", "content_direction", "user_evidence_ids",
                "competitor_checked_listing_ids", "expected_metric", "claim_boundary")
    errors = [f"缺少字段：{field}。" for field in required if not brief.get(field)]
    if errors:
        return errors
    errors.extend(validate_text(brief["content_direction"]))
    if len(set(brief["user_evidence_ids"])) < 3:
        errors.append("至少绑定 3 条不同的原评论 ID。")
    if not brief["competitor_checked_listing_ids"]:
        errors.append("缺少竞品标题审查 ID。")
    if not any(term in brief["expected_metric"] for term in METRIC_TERMS):
        errors.append("预期指标需写明分子/分母或样本量。")
    if "仅" not in brief["claim_boundary"] and "不能" not in brief["claim_boundary"]:
        errors.append("缺少结论边界说明。")
    return errors

