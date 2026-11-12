# API、JSON 与状态传递说明

**版本 v0.7。**默认 API 是本机 `127.0.0.1` 的确定性模拟端点，用于演示“程序 → HTTP API → 模拟模型 → JSON → 程序”的调用链。它不调用外部大模型，也不产生新的消费者语义编码。可通过 `python -m src.marketing_workflow --api-url URL` 改用兼容的 HTTP JSON 服务；密钥若由外部服务要求，应仅通过运行环境或服务端配置传递，本项目代码和日志均不保存密钥。

## 接口

| 接口 | 请求 | 响应 | 错误 |
|---|---|---|---|
| 本地模拟模型 `POST /model` | `{"step":"target_consumer|communication_theme|channel_plan|campaign","context":{...}}` | `{"result":{...}}` | 503 可重试；JSON 错误和字段缺失终止 |
| 页面 `POST /api/run` | `{"request":"给蓝牙耳机设计一次新品推广","source":"课程个人作业","collection_date":"YYYY-MM-DD"}` | 上传元数据、运行目录、状态与 Campaign 草案 | 400 输入错误，500 流程错误 |
| 页面 `GET /api/latest` | 无 | 最近一次正式运行的 `state` 和 Campaign 草案 | 无正式运行时 `not_run` |

模型步骤的必需字段由 `src/marketing_workflow.py` 的 `MODEL_REQUIRED` 逐步检查；状态和 Campaign 结构见 `docs/workflow_schema.json`。证据 ID 还必须存在于本次消费者洞察 JSON 和商品清洗 CSV。传播主题须通过 Brand Voice 检查。字段齐全的 JSON 仍可能需要人工判断业务合理性。

## 状态和文件

每次运行创建 `outputs/runs/<run_id>/`，包含 `01_brand_profile.json` 至 `09_campaign.json`。每个步骤文件记录 `input`、`output`、`status`、`evidence_sources`、开始与结束 UTC 时间。`state.json` 汇总步骤状态，`events.jsonl` 记录状态变化、API 尝试和人工审核点。消费者统计、竞争分数、内容机会分别在同一运行目录的 `consumer_outputs/`、`competition_outputs/`、`content_outputs/`。原始页面输入位于 `data/raw/uploads/`；不会覆盖已有原始文件。

整体状态为 `running`、`failed` 或 `draft_pending_human_review`。Campaign 只能以待人工审核草案状态保存。人工审核需要核对产品测试事实、预算、渠道资源、评论使用范围及对外表述；本实验不含发布或自动批准接口。

## API 重试与兜底

默认每次请求超时 0.5 秒，失败后最多重试 2 次，使用短暂递增等待。HTTP 503、429 与网络或超时错误可重试；仍失败则使用本地确定性模板并在事件日志标注 `deterministic_local_fallback`。JSON 无法解析、缺少 `result`、业务字段缺失或证据 ID 错误不会兜底为成功，而是停止并保存失败状态。请求中的 `context` 只含本项目脱敏样本及前序步骤结果，不含个人资料或密钥。

