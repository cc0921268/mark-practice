# 10 条评论盲测记录

日期：2026-11-10。个人先逐条阅读虚构评论并核对程序输出，检查标签是否有原文证据；遇到规则误判时修订规则，再用固定参考标签复测。参考标签文件为 `tests/expected_labels.json`，完整输出为 `data/sample/example_output.json`。

缩写：S=sentiment，N=need，P=pain_point，C=scenario，B=purchase_barrier；`U` 表示 `unknown`。

| 编号 | 评论关键内容 | 预期与最终实测（S / N / P / C / B） | 证据检查 |
|---|---|---|---|
| R01 | 通勤、方便携带、满意 | positive / portability / U / commute / U | 原文词段匹配 |
| R02 | 漏水、失望 | negative / U / leakage / U / U | 原文词段匹配 |
| R03 | 太贵、暂时不买 | U / U / U / U / price | 不从“不买”猜测情感 |
| R04 | 保温、很好、露营 | positive / warmth / U / outdoor / U | 原文词段匹配 |
| R05 | 包装是蓝色的 | U / U / U / U / U | 纯事实句保持未知 |
| R06 | 不漏水、满意 | positive / U / U / U / U | 否定“漏水”不记痛点 |
| R07 | 喜欢、续航短、失望 | mixed / U / battery / U / U | 情感保留正负两段证据 |
| R08 | 不可信、不敢下单 | U / U / U / U / trust | 仅标注显式信任障碍 |
| R09 | 空评论 | U / U / U / U / U | 全部证据 `null`，置信标记 0.0 |
| R10 | 旅行、太重、不方便携带 | negative / U / weight / travel / U | “方便携带”前有否定，修订后需求保持未知 |

**一致性结果：**修订后 10/10 条的五个标签与参考标签一致；所有非空证据均为对应评论的精确子串，未知标签对应证据均为 `null`。同一输入连续运行的 JSON 内容一致。`python -m unittest discover -s tests -v`：5 项通过；`python tests/api_check.py`：上传、10 条结果、重复结果、缺字段与原始文件留存均通过。

**缺失字段检查：**`data/sample/missing_field.csv` 无 `review` 列，接口返回 400 和“CSV 缺少必需字段：review”，原始上传仍独立留存，未生成成功分析结果。

