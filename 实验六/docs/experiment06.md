# 实验六：Content Gap 与 Brand Voice

**个人作业，版本 v0.6。**

## 第 11 周

从实验四 30 条真实评论编码计算 12 个痛点导出的需求主题提及率；从实验五可排名竞品 Sennheiser 与 Jabra 的 13 条耳机商品标题计算标题覆盖率，并核对 ANC 卖点汇总。生成 `outputs/theme_matrix.csv`、`outputs/opportunity_scores.csv` 与 `outputs/evidence_record.csv`。公式、阈值和口径见 `docs/score_formula.md`。设备可靠性、续航与充电等 6 个主题达标；口味 0/30、0/13，被识别为伪机会。

## 第 12 周

完成同一页面的机会矩阵、证据查看、6 条内容策略 Brief 和 Brand Voice 检查。虚构品牌清波 ClearWave 的人格、常用词、禁用词、句式、正反例和质量规则位于 `skills/brand-voice/SKILL.md` 与 `skills/brand-voice/references/examples.md`。规则由 `src/brand_voice.py` 实际执行，生成 Brief 时若不通过则停止。人类发布审核仍需验证产品事实和评论使用许可。

## GitHub Skill 使用

项目内保存 GitHub [Anthropic `skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 和 [`brand-guidelines`](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) 的原版副本，未修改原版。前者用于设计本地 Skill 并实际调用 `quick_validate.py`，结果为 `Skill is valid!`。后者只作品牌规范结构参考；其专有视觉配色与字体没有套到课程虚构品牌上。

## 验收结果

| 标准 | 证据 |
|---|---|
| 机会公式公开 | `docs/score_formula.md` 与程序中的逐项计算 |
| 每个机会可追溯 | `outputs/evidence_record.csv` 的评论 ID、精确引句、标题 ID 与审查列表 |
| 排除伪机会 | 口味 0/30、0/13，机会分数 0；售后、包装和配送也未达评论门槛 |
| Brand Voice 可执行 | `src/brand_voice.py` 的词汇、句长和 Brief 字段检查，正反例测试 |
| 至少 5 条策略 Brief | 6 条通过规则检查，见 `docs/strategy_briefs.md` 和 JSON |

测试记录见 `docs/test_record.md`。这些机会是非随机小样本和商品标题词匹配的结果，不能代表总体需求或竞品全渠道内容覆盖。



