"""Streamlit entry point for the Bluetooth earbud marketing coursework."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src import system
from src.path_security import project_source
from src.marketing_workflow import run_workflow

st.set_page_config(page_title="蓝牙耳机营销系统", layout="wide")
st.title("蓝牙耳机营销系统 · v1.0")
st.caption("课程研究工具。统计由 Python 计算；评论标签来自有证据的原始标注，陌生评论默认未知。")
system.init_db()

with st.sidebar:
    st.header("数据输入")
    product_file = st.file_uploader("商品 CSV", type="csv", key="products")
    review_file = st.file_uploader("评论 CSV", type="csv", key="reviews")
    st.caption("未上传时使用项目内示例。原始文件不会被覆盖。")
    try:
        products = system.load_products(product_file if product_file else system.PRODUCTS)
        encoded, reviews = system.load_encoded(review_file if review_file else system.REVIEWS)
        brands = sorted(products.brand.dropna().astype(str).unique())
        focal = st.selectbox("研究品牌", brands, index=brands.index("Skullcandy") if "Skullcandy" in brands else 0)
    except Exception as exc:
        st.error(str(exc))
        st.stop()
    run = st.button("运行分析", type="primary", width="stretch")

if run:
    try:
        result = system.analyze(products, encoded, focal)
        st.session_state["analysis"] = result
        st.session_state["focal"] = focal
        system.save_run(focal, "analysis", "completed", {
            "product_rows": len(products), "review_rows": len(reviews),
            "opportunities": result["content"]["summary"]["opportunity_count"]})
    except Exception as exc:
        st.error(f"分析失败：{exc}")

tabs = st.tabs(["品牌档案", "消费者洞察", "竞争情报", "内容机会", "Campaign Planner", "营销效果", "历史与下载"])

with tabs[0]:
    st.subheader("品牌档案")
    st.write(f"当前研究品牌：**{focal}**")
    st.caption("Brand Voice v0.6 是课程中创建的虚构表达规范，并非该品牌官方指南。")
    with st.form("profile"):
        audience = st.text_input("目标人群", "关注佩戴舒适度与连接稳定性的蓝牙耳机用户")
        description = st.text_area("品牌研究备注", "依据公开商品列表与评论样本进行课程分析。")
        if st.form_submit_button("保存品牌档案"):
            system.save_profile(focal, audience, description)
            st.success("已保存到项目内 SQLite。")
    st.dataframe(system.history().query("kind == 'campaign'"), width="stretch")

analysis = st.session_state.get("analysis")
with tabs[1]:
    st.subheader("消费者洞察")
    st.metric("评论样本量", len(reviews))
    st.caption("现有评论使用经原文校验的标签；新 ID 的评论保留 unknown，不推测语义。")
    if analysis:
        st.dataframe(analysis["insight"]["pain_ranking"], width="stretch")
        st.bar_chart(analysis["insight"]["pain_ranking"].set_index("pain_tag")["count"])
        st.dataframe(analysis["insight"]["sentiment_distribution"], width="stretch")
    st.subheader("原文证据")
    brand_filter = st.selectbox("评论品牌", ["全部"] + sorted(reviews.brand.unique()), key="review_filter")
    evidence = pd.DataFrame(encoded)
    if brand_filter != "全部":
        evidence = evidence[evidence.brand == brand_filter]
    st.dataframe(evidence[["review_id", "brand", "review_text", "sentiment", "pain_tags", "evidence"]], width="stretch")

with tabs[2]:
    st.subheader("竞争情报")
    if analysis:
        comp = analysis["competition"]
        st.caption("指数权重：消费者重合 30%，产品重合 25%，价格重合 20%，品牌热度 25%。缺失数据按模块规则处理。")
        st.dataframe(comp["scores"], width="stretch")
        st.bar_chart(comp["scores"].dropna(subset=["threat_index"]).set_index("competitor")["threat_index"])
        st.dataframe(comp["price_bands"], width="stretch")
        st.subheader("指标证据")
        st.dataframe(comp["evidence"], width="stretch")
    else:
        st.info("点击左侧“运行分析”查看排名。")

with tabs[3]:
    st.subheader("内容机会")
    if analysis:
        gap = analysis["content"]
        st.caption("机会分数来自评论主题提及率与竞品商品标题未覆盖率；标题覆盖不代表全部广告内容。")
        if gap["theme_matrix"].empty:
            st.info("证据不足：需要各品牌足量有原文证据的评论标签，才能计算内容机会。")
        else:
            st.dataframe(gap["theme_matrix"], width="stretch")
        st.subheader("策略 Brief")
        for brief in gap["briefs"]:
            with st.expander(f"{brief['theme']} · {brief['opportunity_score']}"):
                st.json(brief)
        st.subheader("来源记录")
        st.dataframe(gap["evidence_record"], width="stretch")

with tabs[4]:
    st.subheader("Campaign Planner")
    st.caption("调用复制到本项目的 Workflow；默认使用本地模拟响应，草案必须经人工审核。此流程读取项目内示例数据。")
    st.info("演练反馈驱动的原型修订：策略展示应说明价格、实测条件与行动入口；下方价格是样本挂牌价，不是成交价。")
    focal_prices = pd.to_numeric(products.loc[products.brand.eq(focal), "price_usd"], errors="coerce").dropna()
    if not focal_prices.empty:
        st.write(f"{focal} 样本挂牌价范围：${focal_prices.min():.2f}–${focal_prices.max():.2f}；样本商品 {len(focal_prices)} 条。")
    st.caption("购买入口需在人工审核后关联真实商品页；续航、佩戴和降噪描述应附实际测试条件。")
    request = st.text_input("策划需求", "给蓝牙耳机设计一次新品推广")
    if st.button("生成 Campaign 草案"):
        try:
            output = run_workflow(request)
            st.session_state["campaign"] = output
            system.save_run(focal, "campaign", output["status"], output["campaign"], output["run_dir"])
        except Exception as exc:
            st.error(f"Workflow 失败：{exc}")
    if "campaign" in st.session_state:
        st.json(st.session_state["campaign"]["campaign"])
        st.caption("审批状态：待人工审核；证据与每步状态保存在 outputs/runs。")

with tabs[5]:
    st.subheader("营销效果分析")
    st.caption("上传匿名 A/B 答卷。演练文件标为模拟，不代表真实参与者。")
    ab_file = st.file_uploader("A/B 或问卷 CSV", type="csv", key="ab")
    source = ab_file if ab_file else ROOT / "data/sample/ab_simulated.csv"
    if source.exists() if isinstance(source, Path) else bool(source):
        try:
            ab = pd.read_csv(project_source(source), encoding="utf-8-sig")
            table, meta = system.analyze_ab(ab)
            st.dataframe(table, width="stretch")
            st.json(meta)
            st.dataframe(ab[["respondent_id", "variant", "feedback"]], width="stretch")
            st.download_button("下载汇总 CSV", table.to_csv(index=False).encode("utf-8-sig"), "ab_summary.csv", "text/csv")
        except Exception as exc:
            st.error(str(exc))

with tabs[6]:
    st.subheader("历史与下载")
    st.dataframe(system.history(), width="stretch")
    if analysis:
        for section, name, key in [("消费者", "pain_ranking", "insight"),
                                   ("竞争", "scores", "competition"),
                                   ("内容", "theme_matrix", "content")]:
            frame = analysis[key][name]
            st.download_button(f"下载{section}结果", frame.to_csv(index=False).encode("utf-8-sig"),
                               f"{name}.csv", "text/csv")
        st.download_button("下载编码 JSON", json.dumps({"records": encoded}, ensure_ascii=False, indent=2),
                           "encoded_reviews.json", "application/json")

