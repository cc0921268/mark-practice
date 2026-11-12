"""Integration layer. All arithmetic is performed here or in copied Python modules."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src import consumer_insight_engine as insight
from src import competitive_intelligence as competition
from src import content_opportunity as content
from src.path_security import project_path, project_source

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "marketing_os.sqlite3"
PRODUCTS = ROOT / "data/processed/clean_data.csv"
REVIEWS = ROOT / "data/raw/reviews.csv"
ANNOTATIONS = ROOT / "data/processed/semantic_annotations.json"


def init_db(path: Path = DB) -> None:
    path = project_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS brand_profile (
            brand TEXT PRIMARY KEY, audience TEXT NOT NULL, voice_version TEXT NOT NULL,
            description TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
            brand TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL,
            summary_json TEXT NOT NULL, artifact_path TEXT);
        """)


def save_profile(brand: str, audience: str, description: str, path: Path = DB) -> None:
    path = project_path(path)
    init_db(path)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("""INSERT INTO brand_profile VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(brand) DO UPDATE SET audience=excluded.audience,
            voice_version=excluded.voice_version, description=excluded.description,
            updated_at=excluded.updated_at""",
            (brand, audience, "v0.6 / 课程虚构表达规范", description,
             datetime.now(timezone.utc).isoformat()))


def save_run(brand: str, kind: str, status: str, summary: dict,
             artifact_path: str = "", path: Path = DB) -> None:
    path = project_path(path)
    init_db(path)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("INSERT INTO runs(created_at,brand,kind,status,summary_json,artifact_path) VALUES (?,?,?,?,?,?)",
                   (datetime.now(timezone.utc).isoformat(), brand, kind, status,
                    json.dumps(summary, ensure_ascii=False), artifact_path))


def history(path: Path = DB) -> pd.DataFrame:
    path = project_path(path)
    init_db(path)
    with closing(sqlite3.connect(path)) as db:
        return pd.read_sql_query("SELECT created_at,brand,kind,status,summary_json,artifact_path FROM runs ORDER BY run_id DESC", db)


def load_products(source=PRODUCTS) -> pd.DataFrame:
    frame = pd.read_csv(project_source(source), dtype={"listing_id": str}, encoding="utf-8-sig")
    required = {"listing_id", "title", "brand", "price_usd", "rating", "reviews_count", "watchers_count", "scrape_date"}
    missing = sorted(required - set(frame))
    if missing:
        raise ValueError("商品 CSV 缺少字段：" + ", ".join(missing))
    if frame.empty or frame.listing_id.isna().any() or frame.listing_id.duplicated().any():
        raise ValueError("商品 CSV 为空，或 listing_id 缺失、重复")
    return frame


def load_encoded(review_source=REVIEWS) -> tuple[list[dict], pd.DataFrame]:
    reviews = insight.load_reviews(project_source(review_source))
    known = {row["review_id"]: row for row in json.loads(project_path(ANNOTATIONS).read_text(encoding="utf-8"))}
    annotations = [known.get(rid, {"review_id": rid, "sentiment": "unknown", "pain_tags": {},
                                   "scenario": "unknown", "purchase_barrier": "unknown"})
                   for rid in reviews.review_id]
    # Existing labels must still pass verbatim evidence checks against uploaded text.
    encoded = insight.encode(reviews, annotations)
    return encoded, reviews


def analyze(products: pd.DataFrame, encoded: list[dict], focal: str) -> dict:
    if focal not in set(products.brand):
        raise ValueError("所选品牌不在商品数据中")
    stats = insight.statistics(encoded, products)
    products = products.copy()
    products["price_usd"] = pd.to_numeric(products["price_usd"], errors="raise")
    products["rating"] = pd.to_numeric(products["rating"], errors="raise")
    products["reviews_count"] = pd.to_numeric(products["reviews_count"], errors="raise")
    products["product_segment"] = products["title"].map(competition._product_segment)
    products["price_band"] = products["price_usd"].map(competition._price_band)
    products["anc_mentioned"] = products["title"].str.contains(r"noise.cancel|\banc\b", case=False, regex=True)
    rivals = competition.calculate(products, encoded, focal)
    selling = rivals["selling_points"]
    if rivals["summary"]["ranked_competitors"]:
        gap = content.calculate(encoded, products, selling, rivals["scores"], focal=focal)
    else:
        gap = {"theme_matrix": pd.DataFrame(), "evidence_record": pd.DataFrame(),
               "briefs": [], "summary": {"opportunity_count": 0,
               "status": "insufficient_labeled_reviews_for_competitor_comparison"}}
    return {"insight": stats, "competition": rivals, "content": gap}


def analyze_ab(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {"respondent_id", "variant", "click_intent", "purchase_intent", "feedback"}
    missing = sorted(required - set(frame))
    if missing:
        raise ValueError("测试 CSV 缺少字段：" + ", ".join(missing))
    data = frame.copy()
    if data.respondent_id.isna().any() or data.respondent_id.duplicated().any():
        raise ValueError("respondent_id 缺失或重复")
    if set(data.variant.dropna()) - {"A", "B"} or set(data.variant.dropna()) != {"A", "B"}:
        raise ValueError("variant 必须同时包含 A 与 B")
    for col in ("click_intent", "purchase_intent"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
        if data[col].isna().any() or not data[col].between(1, 5).all():
            raise ValueError(f"{col} 必须为 1–5 的整数")
    table = data.groupby("variant", as_index=False).agg(
        sample_size=("respondent_id", "nunique"),
        click_mean=("click_intent", "mean"), purchase_mean=("purchase_intent", "mean"),
        click_high=("click_intent", lambda s: int(s.ge(4).sum())),
        purchase_high=("purchase_intent", lambda s: int(s.ge(4).sum())))
    for col in ("click", "purchase"):
        table[f"{col}_high_percent"] = (100 * table[f"{col}_high"] / table.sample_size).round(2)
        table[f"{col}_mean"] = table[f"{col}_mean"].round(2)
    return table, {"sample_size": len(data), "denominator": "各方案有效答卷数",
                   "data_status": "由上传文件提供；系统不推定为真实用户数据"}

