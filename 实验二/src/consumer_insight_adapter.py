"""CSV integration adapter for the published amazon-consumer-insight Skill."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("review_id", "review")
RULES = {
    "sentiment": {"positive": ("满意", "喜欢", "很好", "方便", "不漏水", "好用", "推荐"),
                   "negative": ("失望", "太贵", "续航短", "不方便", "太重", "不好", "差")},
    "need": {"portability": ("方便携带", "便携", "携带"), "warmth": ("保温", "暖")},
    "pain_point": {"leakage": ("漏水", "漏液"), "battery": ("续航短", "电量不足", "电池"), "weight": ("太重", "重量")},
    "scenario": {"commute": ("通勤", "上下班"), "outdoor": ("露营", "户外"), "travel": ("旅行", "旅游")},
    "purchase_barrier": {"price": ("太贵", "价格高", "价格太贵"), "trust": ("不可信", "不信任", "不敢下单")},
}


class AdapterError(ValueError):
    pass


def _match(text: str, rules: dict[str, tuple[str, ...]]) -> tuple[str, str | None]:
    for label, terms in rules.items():
        for term in terms:
            if term in text:
                return label, term
    return "unknown", None


def analyze_reviews_csv(raw: bytes | str, *, source_name: str = "reviews.csv") -> dict:
    """Map course CSV to the published Skill's evidence-first output contract."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)) or not raw:
        raise AdapterError("CSV 文件不能为空")
    try:
        text = bytes(raw).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        missing = [field for field in FIELDS if field not in headers]
        if missing:
            raise AdapterError("CSV 缺少字段：" + ", ".join(missing))
        rows = list(reader)
    except UnicodeDecodeError as exc:
        raise AdapterError("CSV 必须使用 UTF-8 编码") from exc
    ids = [str(row.get("review_id", "")).strip() for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise AdapterError("review_id 不能为空且不能重复")
    records = []
    for row in rows:
        review = str(row.get("review", "") or "").strip()
        evidence: dict[str, object] = {}
        sentiment, quote = _match(review, RULES["sentiment"])
        if quote:
            evidence["sentiment"] = [quote]
        values: dict[str, str] = {}
        for field in ("need", "pain_point", "scenario", "purchase_barrier"):
            label, term = _match(review, RULES[field])
            values[field] = label
            if term:
                evidence[field] = term
        if sentiment == "positive" and values["pain_point"] != "unknown":
            sentiment = "mixed"
        records.append({"review_id": row["review_id"].strip(), "review": review,
                        "sentiment": sentiment, **values,
                        "evidence": evidence or {"sentiment": None, "need": None,
                                                   "pain_point": None, "scenario": None,
                                                   "purchase_barrier": None},
                        "confidence": 0.95 if evidence else 0.0})
    return {"version": "v0.2-adapter", "source": source_name, "records": records}


def analyze_reviews_file(path: str | Path) -> dict:
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise AdapterError("禁止读取实验二项目外文件")
    return analyze_reviews_csv(path.read_bytes(), source_name=path.name)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze_reviews_file(args.csv), ensure_ascii=False, indent=2))
