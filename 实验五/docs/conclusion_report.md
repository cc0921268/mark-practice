# 竞争情报结论报告 v0.5

## 分析范围

以 Skullcandy 为焦点，使用 411 条商品列表和 30 条定向选择的真实评论编码。只有同时出现在两份数据中的品牌进入候选。评论不足 3 条的 Apple、JBL、Sony 显示“不可排名”；Jabra 虽有 12 条评论，但商品列表仅 1 条，已明确警示。指数是本实验的比较工具，不是市场份额或真实消费者重叠率。

## 事实：主要竞争者与威胁来源

基准威胁指数中，**Sennheiser 第 1：61.9547/100**，**Jabra 第 2：25.2570/100**。所有四项分数、样本量与权重见 `outputs/scores.csv`；每项指标的来源字段和示例评论/商品 ID 见 `outputs/evidence.csv`。

Sennheiser 的产品结构重合度 79.3269、价格重合度 71.1538、品牌热度 83.3333，均高于 Jabra 对应的 18.7500、0.0000、16.6667。其相对 Skullcandy 的竞争主要发生在**产品结构和价格带**。证据：商品列表 ID 可在 `outputs/evidence.csv` 的 `product_overlap` 与 `price_overlap` 行追到 `clean_data.csv`；Sennheiser 有 13 条、Skullcandy 有 16 条商品列表。两者在评论中也共同提及电池、连接、设备失效和佩戴问题，例如 Skullcandy 原评论 `R1NZFMP5E3V7DO` 的 “battery low with in thirty minutes” 与 Sennheiser 原评论 `R3KWX129FATHZ5` 的 “2 days to charge fully”。这只支持痛点主题有交集，不能说明顾客相同。

Jabra 的消费者痛点代理重合度为 54.6763，高于 Sennheiser 的 23.5294；共同标签包括电池、连接、设备失效和佩戴。证据示例：Jabra 原评论 `R3LE7R8KC2FNBN` 的 “THEY WILL NOT CHARGE”、`R15KN6XHFIEM00` 的 “disonnect bluetooth and connect again”，Skullcandy 原评论 `R3IJ6RANP5Z9KV` 的 “will not charge”、`R33SEAQBU28DVP` 的 “stopped connecting”。但 Jabra 商品列表只有 1 条，价格带不重合，产品结构分数不稳。**推断：**Jabra 应列为需补充商品样本的观察对象，不宜据当前总分判断其真实市场威胁。

## 事实：价格带、产品结构、评价和卖点

Skullcandy 商品列表 16 条，其中 `<50 USD` 4 条、`50–99.99 USD` 8 条、`100–199.99 USD` 4 条；Sennheiser 13 条，其中 `50–99.99 USD` 6 条、`100–199.99 USD` 4 条、`≥200 USD` 3 条。来源和商品 ID 均可由 `outputs/price_bands.csv` 与 `clean_data.csv` 核对。列表平均评分：Skullcandy 4.72、Sennheiser 4.92、Jabra 4.50；这些是来源列表评分，不是实验四 30 条评论的评分均值。产品形态和标题中 ANC 提及情况见 `outputs/product_structure.csv` 与 `outputs/selling_points.csv`。标题未提及 ANC 不等于没有该功能。

## 市场空白候选与边界

在当前 411 条商品快照中，**`≥200 USD` 且标题明确提及 ANC 的耳塞产品**只有 2 条，占 2/411（0.49%）；商品列表 ID 为 `365966411610` 和 `397462781565`，可由 `outputs/market_gap_segments.csv` 回查。**机会假设：**这是一处低供给组合，值得另行验证需求、销量和实际功能。现有数据没有购买转化或总体市场覆盖率，不能直接称其为可盈利市场空白，也不能从评论痛点推断该价格段的需求。

## 权重变化与结论级别

在四种中等幅度调整中，Sennheiser 仍居首。将消费者代理权重提至 70% 的压力测试，Jabra 升至第 1（42.6484），Sennheiser 为第 2（40.4610），说明排序依赖分析假设。详情见 `docs/sensitivity_check.md`。因此结论分为：**事实**是样本内计数与指数；**推断**是 Sennheiser 在产品和价格层面更接近 Skullcandy；**机会假设**是少见的高价 ANC 标题组合值得后续验证。

