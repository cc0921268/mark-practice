# 语义编码 Prompt v0.4

**任务：**阅读 `review_id` 对应的原始蓝牙耳机评论正文，输出 JSON 数组。AI 只负责语义编码和原文证据，不执行计数、分组、均值、占比或排序；这些操作由 `src/consumer_insight_engine.py` 使用 pandas 执行。

## 输入

每条输入包含 `review_id` 和 `review_text`；可有商品名称、品牌、评分。只能依据 `review_text` 标注，不依据评分推断情绪，也不能把商品列表的价格或抓取日期当作该条评论的属性。

## 输出约束

每条返回 `review_id,sentiment,sentiment_evidence,pain_tags`。`sentiment` 只能是 `positive,negative,mixed,neutral,unknown`。`pain_tags` 是标签到**原文精确子串**的映射；允许值为 `price,taste,delivery,packaging,battery,fit,connectivity,sound,device_failure,noise_cancellation,product_condition,support`。可选 `scenario,scenario_evidence,purchase_barrier,purchase_barrier_evidence`，但标签非未知时必须有原文证据。不得输出评论中没有的时间、身份、行为或购买动机。

四个跨品类标签必须检查：价格、口味、配送、包装。耳机评论通常没有口味，未出现明确抱怨就不要标记。`fast shipping` 是正面配送描述，不能记作配送痛点；充电盒的问题通常是电池或设备问题，不能自动记作包装问题。一个评论可标多个痛点，但同一标签在同一评论只记一次。

无法判断时填 `unknown` 或空 `pain_tags`，不要强行分类。所有证据必须与同一原评论的字节对应文本完全一致。输出仅包含 JSON，不写统计解释。

## 本次执行方式

Codex 按此规则逐条阅读 30 条去标识化真实评论，将标注写入 `data/processed/semantic_annotations.json`。Python 核对 ID 与证据，补齐实验二稳定字段并生成 `outputs/encoded_reviews.json`。洞察解释另见 `docs/ai_explanation.md`，其中所有数字来自 Python 统计表。

