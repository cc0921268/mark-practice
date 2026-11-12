# 测试与个人验收记录

日期：2026-11-10。版本：v0.5。执行方式：个人自测。

| 项目 | 预期与实测 |
|---|---|
| 权重合计 | 基准和 5 个敏感性情景权重均为 100%；单元测试通过。 |
| 小样本排名 | Focus 与 Alpha 的痛点、产品和价格完全重合，Alpha 排第 1；Beta 排第 2。 |
| 手工复算 | Sennheiser 四项分数按 30/25/20/25 加权约为 61.9547，与程序一致。 |
| 缺失处理 | Apple、JBL、Sony 评论不足 3 条，指数为空且不可排名；Jabra 1 条商品列表显示警示。 |
| 证据校验 | 评论痛点证据必须是同一原评论的子串；编造证据的输入被拒绝。 |
| 原始文件保护 | 商品和评论副本哈希在测试前后不变；上传测试的字节与原始留存文件一致。 |
| Dashboard | 首页、焦点品牌重算、同结构上传、输出文件和来源记录通过接口检查。 |
| 敏感性 | 中等权重变化不改变前两名；70% 消费者权重压力测试使 Jabra 与 Sennheiser 互换。 |
| GitHub Skill | 原版 `skill-creator/quick_validate.py` 返回 `Skill is valid!`。 |

运行 `python -m unittest discover -s tests -v`：6 项通过。运行 `python tests/api_check.py`：接口检查通过。完整指标、证据和结论分别见 `docs/metric_dictionary.md`、`outputs/evidence.csv`、`docs/conclusion_report.md`。

