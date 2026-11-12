# 实验五：竞争情报分析引擎

**个人作业，版本 v0.5。**

## 第 9 周

复用实验三的 `clean_data.csv` 和实验四的 `encoded_reviews.json`，固定 SHA-256 并记录来源。定义四项指标、单位、公式、权重和缺失规则，见 `docs/metric_dictionary.md`。先用 `data/sample/mini_products.csv` 与 `mini_encoded_reviews.json` 做小样本排名检查：Focus 与 Alpha 的痛点、产品结构和价格带完全相同，Alpha 排第 1；Beta 的痛点与产品形态不同，排第 2。该样例由测试自动核对，不用于正式结论。

## 第 10 周

完成 `src/competitive_intelligence.py`、`app.py` Dashboard、各项统计表、`outputs/evidence.csv`、`docs/conclusion_report.md` 与 `docs/sensitivity_check.md`。Dashboard 可切换焦点品牌、查看价格带、产品结构、列表评分、标题 ANC 提及、证据 ID 和权重情景。上传同结构数据时原始字节单独保存，输出进入独立运行目录。

## GitHub Skill 调用

从 GitHub [Anthropic `skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 获取原版 Skill 指南、许可证和 `quick_validate.py`，未改动原版。按其结构编写 `skills/competitor-profiling (GitHub)/SKILL.md`，实际运行 GitHub 校验脚本，返回 `Skill is valid!`。运行时只由本地 pandas 计算，不调用大模型 API。

## 验收映射

| 要求 | 证据 |
|---|---|
| 权重合计 100% | 公式说明、`outputs/summary.json` 和单元测试 |
| 排名可复算 | 四项分数与指数存于 `outputs/scores.csv`；手工抽查及小样本测试 |
| 每项指标有来源 | `docs/metric_dictionary.md` 与 `outputs/evidence.csv` |
| 结论可追证据 | `docs/conclusion_report.md` 列出原评论和商品列表 ID |
| 事实、推断、机会假设分开 | 结论报告独立标记，低供给段只称候选 |
| 权重变化可解释 | `outputs/sensitivity.csv` 与 `docs/sensitivity_check.md` |

样本限制：评论仅 30 条且定向选取，商品列表 411 条来自筛选快照；两份输入没有共同消费者或商品标识。不能宣称真实消费者交集或代表总体市场。

