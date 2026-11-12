# 验收与测试记录

日期：2026-11-10。版本：v0.4。执行方式：个人自测。

| 检查 | 结果 |
|---|---|
| 商品清洗数据复现 | `clean_data.csv` SHA-256 与实验三记录完全一致；411 条商品列表。 |
| 评论与证据 | 30 条真实评论 ID 唯一；编码逐条对应原评论；所有引句必须是同条原文的精确子串。 |
| 统计可复算 | `src/consumer_insight_engine.py` 使用 pandas 计算；测试从编码重新计算并与 CSV 统计表比较。 |
| 百分比 | 每行有 `count,denominator,sample_size,percent`；设备失效 9/30=30.00%。 |
| 四类指定痛点 | 价格 4/30、口味 0/30、配送 0/30、包装 1/30；无证据的类别不补造。 |
| 三类边界样例 | 正常 3 条、缺字段、编造引句；正常通过，后两者明确拒绝。 |
| 上传与 Dashboard | HTTP 检查包含首页统计、编码 JSON、3 条样例上传、证据拒绝与原始字节留存。 |
| 编码抽检 | 10 条内部逐条核对一致；独立人工一致率尚待复核，见 `docs/audit_10.md`。 |
| GitHub Skill | 原版 `skill-creator` 的 `quick_validate.py` 实际运行，返回 `Skill is valid!`。 |

执行记录：`python -m unittest discover -s tests -v`，5 项通过；`python tests/api_check.py`，端到端检查通过。所有主结论的至少三条评论 ID 及原文引句见 `docs/insight_report.md`。

