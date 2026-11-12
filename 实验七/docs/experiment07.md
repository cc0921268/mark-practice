# 实验七：AI 营销 Workflow

**个人作业；版本 v0.7。**

## 第 13 周

绘制 `docs/workflow.mmd` 九步流程图，定义步骤输入、输出、状态、证据和人工审核点。`docs/workflow_schema.json` 定义状态、步骤、API 信封及 Campaign 结构，`docs/api_contract.md` 说明本地 HTTP 模拟模型调用链。每次运行的步骤文件可追溯到前序输入与证据 ID。

## 第 14 周

真实调用实验四消费者引擎、实验五竞争引擎、实验六 Content Gap 与 Brand Voice 四个前序组件，生成消费者统计、竞争指数、六条内容 Brief 和待审核 Campaign 草案。故意注入 503、错误 JSON、缺字段与超时，并记录重试、兜底或失败，见 `docs/error_handling.md` 和 `outputs/debug_results.json`。完整运行日志在 `outputs/runs/` 与 `outputs/debug_runs/`。

## GitHub Skill 使用

项目内保存 GitHub [Anthropic `skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 原版指南、许可证及 `quick_validate.py`，未改动原版。创建 `skills/market-entry-orchestration/SKILL.md` 后实际调用 GitHub 脚本校验，返回 `Skill is valid!`。

## 验收边界

本地模拟模型用于可复现的 HTTP/JSON 链路，不代表真实大模型语义理解。模型环节的目标、主题、渠道与 Campaign 是基于前序证据的确定性草案；所有数字来自前序 Python 组件。外部 API 可用时可替换兼容端点，但不得将未经人工审核的草案用于发布。密钥不写入代码或日志。


