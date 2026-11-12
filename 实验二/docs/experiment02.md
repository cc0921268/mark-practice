# 实验二说明：Consumer Insight Skill

**作业形式：**个人作业  
**版本：**v0.2  
**日期：**2026-11-10

## 目标和边界

将评论读取、标签编码、原文证据和未知值处理组织成可重复调用的 Skill。运行时由 `app.py` 加载 `skills/consumer-insight (GitHub)/scripts/analyze.py` 并调用 `analyze_reviews_csv(raw)`。标注采用确定性词规则；只能识别字典列出的显式表达，不能理解任意语义、反讽或复杂否定。结果用于课程方法演示，不用于推断真实消费者总体。

## 第 3 周交付

完成 UTF-8 评论读取、必需列检查、逐条编码、证据引用和空评论处理。标签字典及字段类型位于 `skills/consumer-insight (GitHub)/references/label_dictionary.md`，允许值和结构约束位于 `skills/consumer-insight (GitHub)/schema.json`。输入示例为 `data/sample/reviews.csv`，输出示例为 `data/sample/example_output.json`。

## 第 4 周交付

完成 `skills/consumer-insight (GitHub)/SKILL.md`、上传接口接入、10 条边界样例盲测和修订记录。缺字段、重复编号会拒绝整份 CSV；空评论保留全未知记录。原始上传保存到 `data/raw/`，结果存入 `data/processed/`，处理日志存入 `outputs/`，三者不互相覆盖。

## 数据来源和字段用途

`data/sample/reviews.csv` 是 2026-11-10 为课程自建的虚构评论，不含真实用户身份。`review_id` 用于定位记录，`review` 用于直接引用证据并标注情感、需求、痛点、场景和购买障碍。其他可选列不参与分析。若上传真实公开评论，需在页面填写实际来源和采集日期，并确认使用许可与去标识化。

## GitHub Skill 接入

从 GitHub Anthropic `skills/skill-creator` 取得 `SKILL.md`、许可证和 `quick_validate.py`，保存在 `skills/github-skill-creator/`。按其“明确意图→编写 Skill→准备案例→评估→修订”的流程完成本地 Skill，并实际调用 `quick_validate.py` 校验，结果为 `Skill is valid!`。该 GitHub Skill 指导设计与评估；本项目运行时只调用本地确定性脚本，不调用任何大模型 API。来源：[GitHub skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)。

## 验收映射

| 标准 | 证据 |
|---|---|
| 输出字段稳定 | `schema.json`、10 条样例、结构测试 |
| 证据来自原文 | 单元测试逐字段检查证据为原文子串，未知字段证据为 `null` |
| 重复运行一致 | 单元测试和两次 HTTP 上传结果一致 |
| Skill 可被项目调用 | `app.py` 从 Skill 脚本加载 `analyze_reviews_csv`；端到端上传通过 |
| 盲测说明问题与修订 | `docs/blind_test.md`、`docs/revisions.md` |


