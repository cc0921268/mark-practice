# 故障、处理与 Debug 记录

真实演练的机器可读结果在 `outputs/debug_results.json`；每例的步骤 JSON、状态和 `events.jsonl` 保存在对应 `outputs/debug_runs/` 目录。复跑：`python tests/debug_scenarios.py`。

| 注入情形 | 期望 | 实测处理 | 用户可读提示/日志 |
|---|---|---|---|
| 第一次 HTTP 503 | 重试一次后成功 | `api_503_once`：第二次调用返回结果，后续九步完成 | 事件日志保留两次尝试及 503 原因 |
| 持续 HTTP 503 | API 不可用时兜底 | `api_unavailable`：重试耗尽，本地确定性模板继续 | 步骤输出注明 `deterministic_local_fallback` |
| JSON 格式错误 | 不使用不可信响应 | `invalid_json`：步骤失败、流程状态 failed | “API 返回的 JSON 无法解析” |
| JSON 缺字段 | 拒绝不完整结果 | `missing_field`：步骤失败、流程状态 failed | “target_consumer 的 JSON 缺少必需字段：segment, why, evidence_ids” |
| 超时 | 有界重试并兜底 | `timeout`：重试耗尽，本地模板继续 | 事件日志保留超时尝试与兜底原因 |

调试中曾发现错误 JSON 被普通 API 异常捕获并错误地进入兜底。修订为 `InvalidResponseError`，只对连接/服务失败使用兜底；缺字段仍由流程字段检查拒绝。故障演练及 5 项单元测试复验通过。API 失败后的草案仍待人工审核，兜底不是人工批准。

