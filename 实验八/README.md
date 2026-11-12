# 实验八：蓝牙耳机营销系统 v1.0

个人课程作业。系统包含品牌档案、消费者洞察、竞争情报、内容机会、Campaign Planner、营销效果分析。所有统计由 Python 完成。Campaign 默认使用本地模拟 HTTP 响应，结果为待审核草案。

## 启动

在本目录运行，虚拟环境保存在本项目内：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_app.py
```

页面打开后点击左侧“运行分析”；可上传符合字段规范的商品与评论 CSV。运行 `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` 可验证核心计算。运行 `.\.venv\Scripts\python.exe -m src.build_artifacts` 可重建演练数据及静态输出。

请使用 `run_app.py` 启动。它在导入 Streamlit 前把用户配置目录映射到项目内；直接执行 `python -m streamlit run app.py` 不受此隔离保护。

## 输入与操作

商品 CSV 必须有 `listing_id,title,brand,price_usd,rating,reviews_count,watchers_count,scrape_date`。评论 CSV 必须有 `review_id,product_name,brand,rating,review_text,review_date,helpful_count`。已有评论使用项目内 `semantic_annotations.json` 的标注，并再次校验证据原文；新 ID 评论的语义字段保持 `unknown`。筛选与分析在内存副本中进行，不覆盖输入文件。上传商品与评论后可在前四页查看结果与证据；Campaign 页运行示例数据的既有 Workflow；营销效果页上传匿名 A/B CSV。

A/B 文件必须有 `respondent_id,variant,click_intent,purchase_intent,feedback`，其中 variant 为 A/B，意愿为 1–5 分。未上传时只展示明确标为 `SIMULATED` 的 24 条演练数据。真实答卷应由本人在取得自愿反馈后导入；不能把演练结果报告为真实用户效果。

## 模块与边界

- `src/consumer_insight_engine.py`：评论编码结果验证、痛点与情绪统计，保留评论 ID。
- `src/competitive_intelligence.py`：竞争威胁指数，权重 30%/25%/20%/25%。
- `src/content_opportunity.py`：评论主题与竞品商品标题覆盖比较。标题不能代表全部广告内容。
- `src/brand_voice.py` 与 `skills/brand-voice`：课程虚构品牌表达规范，不是 Skullcandy 官方指南。
- `src/marketing_workflow.py`：复用洞察、竞争、机会、Brand Voice 等组件，保存步骤状态与证据；默认本地模拟响应。
- `src/system.py`：上传数据适配、SQLite、A/B 指标。新数据若缺少足够有证据的评论标签，部分竞争与内容指标可能不可计算，并显示错误。

SQLite 位于 `data/marketing_os.sqlite3`，记录品牌档案、运行时间和摘要。Workflow 每次运行的详细结果位于 `outputs/runs/`。输出表可在页面下载。

## 数据与合规

项目内商品表为蓝牙耳机公开商品列表的前序实验副本，评论表为前序实验样本副本。两类数据粒度不同，只按品牌对照，不把商品列表与评论假设为同一交易。来源文件、哈希与已知限制见 `docs/source_and_ethics.md`。数据中不含姓名、联系方式等个人敏感字段。原始数据独立保存；运行程序不会写回原始 CSV。

## 交付状态

`docs/` 含字段映射、集成冲突、测试方案与结果、迭代记录、演示脚本和答辩稿。真实 20–30 人用户测试、独立评分及现场录制视频尚需真实参与者与录制操作；现有材料均明确标注演练。版本标记见 `VERSION`。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.


