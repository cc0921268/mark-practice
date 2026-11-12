# 来源、日期、关联边界与伦理记录

**作业形式：**个人作业。**版本：**v0.4。**本地导入日期：**2026-11-10。

## 商品列表

从公开 [eBay Headphones Market Dataset](https://github.com/Haseeb-U/ebay-headphones-market-dataset) 的固定 Git blob `a652532a226278f4cba856efdcd97b2cf62cf2d7`，在实验四内部复现实验三的 480 条抽取及 411 条清洗结果。`data/processed/clean_data.csv` 的 SHA-256 为 `0c4b8a908618cb0a6ae65bb93e5a5355a37eb1e0f1f04f356e9b72b5b986fe55`，与实验三已记录值完全一致。原数据集声明 CC BY-NC 4.0，仅供非商业教育研究；本项目只用于课堂。复现日志见 `outputs/product_reproduction.json`。

## 真实评论

评论取自公开仓库 [Wireless Earbuds Sentiment Analysis](https://github.com/vfabuluje/beats-sentiment-analysis) 的 [`earbuds_reviews_prepared_for_analysis.csv`](https://github.com/vfabuluje/beats-sentiment-analysis/blob/1f2c0667d1f56fd31946463a51bbe0cce0441a4f/earbuds_reviews_prepared_for_analysis.csv)，固定 commit `1f2c0667d1f56fd31946463a51bbe0cce0441a4f`、blob `691f1f4651237049622435cdafd0f6de659dfab6`。源文件 SHA-256 为 `40c1c3885bb4e8f979e9ea1971f216a0ab6255c825cd95141ec81324ccedd3c7`。该仓库说明评论来自 Amazon 无线耳机商品，项目未明确给评论数据另设再发布许可；因此本项目仅作非商业课堂分析，保留来源，不用于商业发布或二次传播。

`src/prepare_reviews.py` 按固定的 30 个原评论 ID 抽取正文、商品名称、品牌、评分和互动计数；不导入 `author`、`profile_id`，也不保留完整源文件。去标识化样本位于 `data/raw/reviews.csv`，SHA-256 为 `cc718b222c66ca7477c12890d41db5257a8b6ff656366d0383f8bcbb72278796`。其时间列 30/30 为空，处理后的 `review_date` 为 `null`，不得使用评论文字提及的月份充当评论发布日期。

## 关联与结论边界

两份数据来自不同平台与来源，缺少共同商品 ID。品牌对比是两个独立样本的并列展示，不是逐条商品或交易关联。30 条评论是针对边界和投诉的定向样本，不是随机样本；百分比仅描述该样本。商品抓取日期不是评论日期。耳机评论没有口味痛点证据，标签保留为 0 而不编造。

## 伦理检查

| 检查 | 处理 |
|---|---|
| 公开可访问与来源 | 两个来源的 URL、固定版本和哈希已记录。 |
| 敏感信息最小化 | 不导入卖家字段、评论作者或个人资料编号；只保留商品与评论正文及汇总计数。 |
| 原始数据保护 | `data/raw/` 使用新建写入；上传原始字节及 AI 编码分别保存，运行统计不覆盖它们。 |
| 存储分离 | 商品和评论原始文件在 `data/raw/`，清洗及语义编码在 `data/processed/`，统计表与日志在 `outputs/`。 |
| 自动化边界 | AI 负责语义标签与解释；Python 负责所有数字；不调用大模型 API。 |

