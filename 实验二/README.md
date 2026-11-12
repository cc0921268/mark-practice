# 实验二：Consumer Insight Skill v0.2

个人作业。该项目在独立的 `实验二` 文件夹内实现评论 CSV 上传、确定性标签标注和结构化 JSON 输出，不调用大模型 API。上传流程沿用实验一的设计：校验元数据、原始字节独立留存、分析结果和处理日志分开保存；实验一文件未被读取或修改。

## 启动

需要 Python 3.10 或更新版本，无需安装第三方包。

```powershell
cd "$HOME\Desktop\实验二"
python app.py
```

在浏览器打开 `http://127.0.0.1:8502`。选择 `data/sample/reviews.csv`，填写来源“课程自建样例”和采集日期，点击“上传并分析”。页面显示 10 条结果，可下载 JSON。另一个样例 `data/sample/missing_field.csv` 用于查看缺字段提示。退出时按 `Ctrl+C`。

## 输出口径

CSV 必需列为 `review_id,review`；编号不可为空或重复。每条结果固定包含 `sentiment,need,pain_point,scenario,purchase_barrier,evidence,confidence`，以及原始编号和评论。证据只取原评论中的原词段。没有足够证据时标签为 `unknown`、证据为 `null`。`confidence` 只表示规则是否命中，不是统计概率。标签定义见 `skills/consumer-insight (GitHub)/references/label_dictionary.md`，Schema 见 `skills/consumer-insight (GitHub)/schema.json`。

上传的原始 CSV 以新文件保存到 `data/raw/`，不覆盖；分析 JSON 存在 `data/processed/`，处理日志存在 `outputs/processing_log.jsonl`。仅上传公开或获准使用、结构清晰且无个人敏感信息的评论。页面上的示例为自建虚构数据。

## 验收

```powershell
python -m unittest discover -s tests -v
python tests\api_check.py
```

10 条输入在 `data/sample/reviews.csv`，对应固定输出示例在 `data/sample/example_output.json`。逐条盲测结果见 `docs/blind_test.md`；误判与修订见 `docs/revisions.md`；实验说明见 `docs/experiment02.md`。

`skills/consumer-insight (GitHub)/SKILL.md` 是本实验交付的可调用 Skill。设计流程参考项目内保存的 GitHub [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 开源 Skill。`v0.2` 为课程版本标记。

GitHub Skill 自带的 `quick_validate.py` 已在本项目内运行并返回 `Skill is valid!`。如需重复校验，可在 PowerShell 中执行：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\consumer-insight (GitHub)
```

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.




### GitHub adapter

The runnable CSV path is `src/consumer_insight_adapter.py`, an integration adapter for the published `funewa/amazon-consumer-insight` Skill. It uses the course CSV fields and keeps unmatched evidence as `unknown`; it is not a new Skill definition.
