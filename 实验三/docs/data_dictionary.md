# 数据字典 v0.3

`data/raw/raw_data.csv` 为从来源记录中直接选出的 480 条，字段值未做清洗；`data/processed/clean_data.csv` 为清洗后的 411 条。所有数值均是商品列表快照，不是交易实绩。源文件没有评论正文。数据字典中的“必填”指本项目选取的分析字段，并不表示原仓库所有行都完整。

| 原始字段 | 类型 | 用途与来源含义 | 清洗后字段 |
|---|---|---|---|
| `listing_id` | 字符串 | 商品列表去重键，不是用户编号 | `listing_id` |
| `title` | 字符串 | 商品名称、筛选耳机类型 | `title` |
| `brand` | 字符串 | 品牌维度；保留源值供核查 | `brand`，精确别名标准化 |
| `price` | 十进制数文本 | 列表标价 | `price_usd`，两位小数 |
| `currency` | 字符串 | 货币类型；仅保留 USD | 不保留，输出价格字段已标明 USD |
| `rating` | 十进制数文本 | 商品评分，不是个人评论情感 | `rating`，一位小数 |
| `reviews_count` | 非负整数文本 | 评论数量，属于汇总互动指标 | `reviews_count` |
| `watchers_count` | 可空非负整数文本 | 商品关注数，属于汇总互动指标；缺失保持空白 | `watchers_count` |
| `scrape_timestamp` | ISO 日期时间文本 | 来源抓取时间，无可靠时区信息 | `scrape_date`，只保留日期 |
| `wireless` | `1.0`、`0.0` 或空白 | 来源的无线属性标记 | 不直接输出，筛选证据见下一行 |
| `bluetooth_evidence` | 枚举 | `explicit_title` 或 `wireless_flag_proxy` | 同名字段；用于提示样本边界 |
| 无 | 布尔文本 | 按价格分布计算异常值，异常仅标记不删除 | `price_outlier` (`true`/`false`) |

源文件还含卖家用户名、卖家位置、列表 URL、卖家反馈等字段，本项目均不导入。`reviews_count` 不能代替评论文本，`scrape_date` 不能代替评论发布时间。清洗结果的八个分析字段为 `listing_id,title,brand,price_usd,rating,reviews_count,watchers_count,scrape_date`；总体完整率按这些字段非空单元格计算。其余两个字段为来源边界与质量标记，不计入完整率。

