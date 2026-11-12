# 实验五：蓝牙耳机竞争情报引擎 v0.5

个人作业。项目根据实验三的 411 条清洗商品列表和实验四的 30 条真实评论标签，计算四项竞争指标、威胁指数、权重敏感性与证据表，并提供本地 Dashboard。前四个实验文件夹没有被修改；本项目使用其交付文件的独立副本。

## 启动

需要 Python 3.10+ 和 pandas 2.x–3.x。当前验证环境为 pandas 3.0.6。

```powershell
cd "$HOME\Desktop\实验五"
python src\competitive_intelligence.py
python app.py
```

浏览器打开 `http://127.0.0.1:8505`。可查看竞品排名、价格带、产品结构、列表评分、标题 ANC 提及、证据 ID 与敏感性情景；可切换焦点品牌。退出时按 `Ctrl+C`。

默认焦点品牌是 Skullcandy。基准公式：`威胁指数 = 消费者关注痛点重合度×30% + 产品结构重合度×25% + 价格重合度×20% + 品牌热度×25%`。四项均为 0–100 分，权重合计 100%。详细公式、单位、来源与缺失规则见 `docs/metric_dictionary.md`。少于 3 条评论的品牌不排名；商品列表少于 3 条的品牌显示警示。这里的“消费者重合度”只是痛点分布代理，**不是同一批消费者的交集**。

## 输出与复算

`python src\competitive_intelligence.py` 重算 `outputs/scores.csv`、`outputs/evidence.csv`、价格带、产品结构、评分、标题卖点、市场空白候选以及 `outputs/sensitivity.csv`。当前基准下 Sennheiser 第 1，Jabra 第 2；Jabra 仅 1 条商品列表，需要谨慎。结论与来源 ID 见 `docs/conclusion_report.md`；权重变化见 `docs/sensitivity_check.md`。

```powershell
python -m unittest discover -s tests -v
python tests\api_check.py
```

第 9 周小样本输入在 `data/sample/`，用于核对手工可解释的排名。Dashboard 上传时需同时提供同结构商品 CSV 与已完成语义编码 JSON，并填写来源和采集日期；原始上传保存在 `data/raw/uploads/`，结果单独存于 `outputs/runs/`，不覆盖基准数据。上传组件负责校验、留存与计算，不执行语义编码。

项目内保存了 GitHub 原版 `skill-creator`，并实际运行其 `quick_validate.py` 验证 `skills/competitor-profiling (GitHub)/SKILL.md`。复验命令：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\competitor-profiling (GitHub)
```

`v0.5` 为课程版本标记。数据与伦理边界见 `docs/source_record.md`；样本不是随机抽样，不能据指数推断真实市场份额或总体消费者行为。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.


