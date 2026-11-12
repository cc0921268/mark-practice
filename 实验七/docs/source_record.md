# 前序数据与组件来源记录

个人作业，版本 v0.7。实验七从前期实验**只读复制**交付文件到自身目录；没有修改实验一至实验六。原评论来源为公开无线耳机评论的脱敏课堂样本，商品来源为公开耳机列表的筛选快照。样本均非随机，无法识别消费者交集或逐商品评论关联。

| 组件或数据 | 本项目副本 | 用途 |
|---|---|---|
| 实验四消费者统计 | `src/consumer_insight_engine.py` | 真实调用 `run`，计算 30 条评论的痛点及情绪分布 |
| 实验五竞争计算 | `src/competitive_intelligence.py` | 真实调用 `load_inputs`、`calculate`、`sensitivity` 和 `write_outputs` |
| 实验六内容机会 | `src/content_opportunity.py` | 真实调用 `load_inputs`、`calculate` 和 `write_outputs` |
| 实验六 Brand Voice | `src/brand_voice.py` | 真实调用 `validate_brief` 和 `validate_text` |
| 原评论及编码 | `data/raw/reviews.csv`、`data/processed/semantic_annotations.json`、`encoded_reviews.json` | 评论 ID、原文引句与语义编码 |
| 商品与卖点 | `data/processed/clean_data.csv`、`selling_points.csv` | 411 条商品列表、竞品标题与卖点核对 |

源文件的 SHA-256 记录在每次 `consumer_outputs/summary.json`、`competition_outputs/summary.json` 与 `content_outputs/summary.json`。实验四评论没有可靠的评论日期，实验三商品抓取日期不是评论日期。Campaign 只作为假设与内容试验计划，不代表产品性能已经证实。

