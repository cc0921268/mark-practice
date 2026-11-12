# 实验七：蓝牙耳机新品推广 Workflow v0.7

个人作业。九步流程依次完成品牌资料、消费者洞察、竞争分析、Content Gap、Brand Voice、目标消费者、传播主题、渠道计划和 Campaign 草案。四个前序组件在本项目内的独立副本被**真实调用**；前六个实验文件夹未被修改。默认使用本地 HTTP 模拟模型演示 API 与 JSON 状态传递，不调用外部大模型 API。

## 启动

需要 Python 3.10+ 和 pandas 2.x–3.x。本次在 pandas 3.0.6 验证。

```powershell
cd "$HOME\Desktop\实验七"
python -m src.marketing_workflow "给蓝牙耳机设计一次新品推广"
python app.py
```

打开 `http://127.0.0.1:8507`。页面可输入需求、来源与日期，运行流程并查看九步状态和 Campaign 草案。退出服务按 `Ctrl+C`。命令行模式每次运行会打印独立的 `outputs/runs/<run_id>/` 路径。

## 输出与审核

每步保存输入、输出、状态、时间和证据来源；`state.json` 汇总状态，`events.jsonl` 记录 API 重试、兜底及人工审核点。消费者、竞争和内容机会统计分别保存在同一运行目录的独立子目录。最新草案另存 `outputs/campaign_strategy.json`，可读策略见 `docs/campaign_strategy.md`。

Campaign 一律为 `pending_human_review`，**不会自动批准或发布**。审核需核查产品实测、评论引用范围、预算和渠道资源。清波 ClearWave 是课程虚构品牌，与竞争分析的焦点品牌 Skullcandy 不同。样本是定向抽取，不能据此推断总体市场。

## 接口与 Debug

工作流图在 `docs/workflow.mmd`，JSON Schema 在 `docs/workflow_schema.json`，接口说明在 `docs/api_contract.md`，异常处理表在 `docs/error_handling.md`。API 默认 0.5 秒超时、最多重试 2 次；503、网络不可用或超时可用确定性本地兜底，错误 JSON 和缺字段会失败并写日志。可选 `--api-url` 指向兼容的 HTTP JSON 服务；本项目代码和日志不写入密钥。

```powershell
python -m unittest discover -s tests -v
python tests\debug_scenarios.py
python tests\api_check.py
```

五类故障演练的结果在 `outputs/debug_results.json`，每例完整运行日志在 `outputs/debug_runs/`。

本实验从 GitHub 获取原版 `skill-creator`，根据其结构创建 `skills/market-entry-orchestration/SKILL.md`，并实际调用其 `quick_validate.py`，结果为 `Skill is valid!`。复验：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\market-entry-orchestration
```

`v0.7` 是课程版本标记，不依赖 Git 标签。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.



