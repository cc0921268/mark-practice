# 字段映射与版本

| 来源 | 字段 | 系统用途 | 缺失处理 |
|---|---|---|---|
| 商品清洗表 | listing_id、title、brand | 商品证据、品牌及产品结构 | 拒绝缺列、空 ID 与重复 ID |
| 商品清洗表 | price_usd、rating、reviews_count、watchers_count、scrape_date | 价格、评分、热度、时间比较 | 数值无效时停止相关统计 |
| 评论表 | review_id、review_text、brand | 原文证据与品牌比较 | 缺列、空原文或重复 ID 时拒绝 |
| 评论标注 | sentiment、pain_tags、evidence | Python 分组计数与追溯 | 新 ID 保留 unknown；证据不在原文则拒绝 |
| 测试答卷 | respondent_id、variant、click_intent、purchase_intent、feedback | A/B 分组与意愿统计 | 缺列、重复 ID、越界分值时拒绝 |

本版统一使用 `review_id`、`listing_id` 作可追溯键；价格为美元挂牌价，非成交价。评论日期为空时不输出评论时间趋势。版本：v1.0。

