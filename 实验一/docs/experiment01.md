# 实验 1：Codex 协作开发与 Debug

**作业形式：**个人作业  
**版本：**v0.1（课程版本标记，不使用 Git 标签）  
**日期：**2026-11-10

## 需求卡

| 项目 | 内容 |
|---|---|
| 营销问题 | 比较不同品牌的商品平均价格和平均评分，辅助发现品牌定位差异。 |
| 目标人群 | 需要快速检查品牌表现的营销人员或课程验收者。 |
| 输入 | UTF-8 CSV；教师数据建议字段 `brand,product,price,rating,sales`。 |
| 必需字段 | `brand`、`price`、`rating`。 |
| 指标口径 | 对每个品牌的有效记录计算算术平均价格和算术平均评分；结果保留两位小数。 |
| 无效值处理 | 必需字段为空、数值非法或价格为负的行跳过，界面显示跳过数和行号。 |
| 结论边界 | 仅做描述性比较；未按销量加权，不推断销量、因果关系或人群偏好。 |

## 两周完成内容

第 1 周：建立规定目录、需求卡和最小可运行上传校验程序。  
第 2 周：完成均值计算、品牌筛选、柱状图、三类 CSV 测试和 Debug 记录。

## 数据来源与用途

`data/sample/` 三套 CSV 为本实验自建虚构商品测试数据，创建日期 2026-11-10，仅用于功能验收，不含个人信息。教师的 `marketing_data.csv` 未随本次输入提供，因此未擅自复制或伪造；拿到文件后可由页面上传，填写教师来源与实际采集日期。每次上传的原始字节保存在 `data/raw/`，文件名使用时间戳和 SHA-256 前缀；结果 JSON 在 `data/processed/`，处理日志在 `outputs/processing_log.jsonl`。`brand` 用于分组与筛选，`price` 用于平均价格，`rating` 用于平均评分；`product` 和 `sales` 原样保留但不参与本实验计算。

## 输入输出规范

输入：小于等于 5 MB 的 UTF-8 CSV，第一行为表头，来源和采集日期必填。  
输出：网页中的品牌汇总表及两个柱状图；成功上传后单独存储原始 CSV、分析 JSON 与处理日志。字段不完整时返回明确错误，原始上传仍留档。

## GitHub Skill 使用记录

使用 Anthropic 开源仓库中的 [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) Skill，项目副本在 `skills/webapp-testing/`，用于指导本地 Web 应用的浏览器测试和截图。已先运行 `with_server.py --help`，然后使用其服务生命周期脚本完成页面验收。Skill 的许可证见同目录 `LICENSE.txt`。未调用任何大模型 API。

## 验收依据

见 `docs/test_record.md`、`docs/debug_log.md` 和 `outputs/` 中的页面截图。品牌筛选只改变浏览器内的显示数组，上传原始文件的 SHA-256 在处理记录中保存，程序无任何覆盖原始文件的写入路径。
