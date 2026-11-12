# 数据来源与采集记录

**作业形式：**个人作业  
**版本：**v0.3  
**本地导入日期：**2026-11-10（UTC 见 `outputs/collection_log.json`）

| 项目 | 记录 |
|---|---|
| 竞争问题 | 无线耳机商品的品牌、定价与评分如何分布？关注数和评论数如何随商品列表变化？ |
| 公开来源 | [eBay Headphones Market Dataset](https://github.com/Haseeb-U/ebay-headphones-market-dataset)；项目作者说明源自公开 eBay 商品列表。 |
| 源文件 | [`dataset/ebay_headphones_listings.csv`](https://github.com/Haseeb-U/ebay-headphones-market-dataset/blob/18fb2f845f9d0ff7a6659884c6d9b6fae2c7111c/dataset/ebay_headphones_listings.csv)，原始仓库共 13,142 条、28 列。 |
| 固定版本 | commit `18fb2f845f9d0ff7a6659884c6d9b6fae2c7111c`；Git blob `a652532a226278f4cba856efdcd97b2cf62cf2d7`。 |
| 源文件校验 | SHA-256：`a94195f6ec773c6f460c66507ea8612a8b1e50e8ad6620d38dd6a1663717f4e7`。 |
| 来源采集时间 | 来源仓库说明为 2026 年 1 月的一次抓取；记录自身的 `scrape_timestamp` 为具体时间。不能把本地导入日期当成商品上架日期或评论日期。 |
| 数据许可 | [DATA_LICENSE.txt](https://github.com/Haseeb-U/ebay-headphones-market-dataset/blob/18fb2f845f9d0ff7a6659884c6d9b6fae2c7111c/DATA_LICENSE.txt) 标为 CC BY-NC 4.0，仅限非商业教育与研究用途；项目内副本 `docs/source_DATA_LICENSE.txt`。 |
| 导入方式 | `src/collect.py` 从公开 GitHub API 获取固定 blob、校验 blob SHA，再按固定规则抽取。未访问站点账户、没有调用大模型 API。 |

## 抽样口径

按源文件顺序取前 480 条满足以下条件的行：标题含 `Bluetooth`，或标题含 `Wireless` 且源文件 `wireless=1.0`；同时 `listing_id,title,brand,price,rating,reviews_count,scrape_timestamp` 非空。两种证据分别记为 `explicit_title` 和 `wireless_flag_proxy`。代理类别只能说明源文件标注为无线，不能证明具体蓝牙协议。原始样本包含重复列表编号，清洗时按规则去重。

这是一份为数据管线练习而筛选的非随机子集。评分和品牌非空是抽取条件，因此完整率不能代表源仓库或市场总体；不能用它推断所有蓝牙耳机的平均价格或消费者偏好。来源没有评论原文，只有评论数量；不伪造评论或评论日期。

源仓库 README 的原文副本保存在 `docs/source_README.md` 供溯源。导入时临时下载的完整 blob 在筛选后已清除，项目只保留去除卖家字段的 480 条原始抽取数据。

