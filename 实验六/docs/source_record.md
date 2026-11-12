# 数据来源与结论边界

**个人作业，版本 v0.6。**本项目只在桌面 `实验六` 内写文件，前五个实验文件夹没有被修改。下列文件均为已有实验交付文件的独立副本。

| 输入 | 项目内位置 | 来源与 SHA-256 | 用途 |
|---|---|---|---|
| 30 条去标识化真实评论编码 | `data/processed/encoded_reviews.json` | 实验四同名输出；SHA-256 `70f7137cabf414d48a19f4fdb1b005062b3595bdf593f87fbfddbb6ee84206bb` | 从原评论 ID 与 `pain_tags` 计算用户主题提及率，追溯精确原文引句 |
| 411 条清洗商品列表 | `data/processed/clean_data.csv` | 实验五副本，其源头为实验三；SHA-256 `0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55` | 读取 Sennheiser 与 Jabra 的商品标题并逐条审查主题词 |
| 竞品标题卖点汇总 | `data/processed/selling_points.csv` | 实验五 `outputs/selling_points.csv`；SHA-256 `3fafc51596f5c2dcc5052f81acafa374ed4d52ab1e5379d644aa714245328ac9` | 与标题中的 ANC 提及数作一致性核对 |
| 竞品排名 | `data/processed/scores.csv` | 实验五 `outputs/scores.csv`；SHA-256 `c5352b867d32a73a2875b95733ed9eedd2cbd0cf199be67bb3665b86126703ce` | 确定本次基准中的两名可排名竞品 |

实验五默认焦点品牌为 Skullcandy，可排名竞品为 Sennheiser 和 Jabra。其标题共 14 条；编号 `376303871056` 是蓝牙 USB Dongle 而不是耳机，被排除后审查分母为 **13 条商品标题**。排除记录位于 `outputs/excluded_accessories.csv`。实验五卖点表的 ANC 提及总数为 2，与排除前商品标题重新扫描结果一致。

原评论来源是公开无线耳机评论数据的去标识化课堂样本，30 条为定向抽取，不代表总体用户比例；商品列表源于公开快照，竞品标题不是完整广告、详情页或营销内容。标题没有某个词只代表**本次标题扫描未命中**，不能断言竞品完全没有相关内容。无共同商品 ID，也无消费者身份信息。品牌清波 ClearWave 是课程虚构品牌，Brand Voice 不是 Skullcandy 的官方风格。所有产物仅供非商业课程学习。

