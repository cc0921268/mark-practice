# 实验四：AI + Python 消费者洞察引擎

**个人作业，版本 v0.4。**

## 第 7 周

在独立的实验四项目内复现实验三商品清洗文件并核对哈希；选取 30 条真实评论并去掉作者与个人资料字段。按照实验二的稳定字段与证据约束，AI 逐条写出 `data/processed/semantic_annotations.json`。`src/consumer_insight_engine.py` 解析编码 JSON、检查原文证据，并用 pandas 完成读取、筛选、分组、计数、占比和排序。准备正常、缺字段、编造引句三类测试输入。

## 第 8 周

完成 `app.py` Dashboard 的痛点排行、情绪分布、品牌对比、商品抓取日期视图和按原评论 ID 查看证据。AI 只根据程序统计表撰写 `docs/ai_explanation.md`，按事实、推断、建议分开。10 条内部编码抽检见 `docs/audit_10.md`；独立人工一致率不虚报。

## 流程

`真实评论 data/raw/reviews.csv → 字段清洗 data/processed/clean_reviews.csv → AI 语义编码 data/processed/semantic_annotations.json → Python 校验与 pandas 统计 outputs/*.csv → Dashboard 与报告 → review_id 证据追溯`。

商品列表 `data/processed/clean_data.csv` 是并列参照数据，来自与实验三相同的固定公开源并在本项目精确复现；它没有评论正文，与评论文件也没有可验证的逐商品连接。评论时间缺失，Dashboard 明示不可比较评论趋势。

## GitHub Skill 使用

GitHub [Anthropic `skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 的原版指南、许可证与 `quick_validate.py` 独立保存在 `skills/github-skill-creator/`，未改动原版。按其结构编写本实验适配的 `skills/consumer-insight (GitHub)/SKILL.md`，实际运行 GitHub 脚本，结果 `Skill is valid!`。运行时不调用大模型 API。

## 统计与解释分工

AI 负责读评论、给标签、选取原文证据，并根据已生成的统计表写解释；Python 拒绝无效证据并计算所有数字。报告中的分母、样本量和排序以 `outputs/` 的机器可读表为准。没有独立人工复核时，不将内部抽检称为正式人工一致率。

