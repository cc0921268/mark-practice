# 实验六：Content Gap 与 Brand Voice v0.6

个人作业。项目把实验四的真实评论痛点编码与实验五的竞品商品标题、卖点汇总结合，生成需求—标题覆盖矩阵、内容机会分数和 6 条有证据的策略 Brief；虚构品牌清波 ClearWave 的 Brand Voice 由独立 Skill 和 Python 校验函数实现。前五个实验文件夹没有被修改。

## 启动

需要 Python 3.10+ 和 pandas 2.x–3.x；当前验证环境为 pandas 3.0.6。

```powershell
cd "$HOME\Desktop\实验六"
python src\content_opportunity.py
python app.py
```

浏览器打开 `http://127.0.0.1:8506`。页面同时显示机会排行、需求—竞品标题矩阵、六条 Brief、按主题查看证据和 Brand Voice 文字检查。退出时按 `Ctrl+C`。

## 输入与口径

输入副本位于 `data/processed/`：实验四的 `encoded_reviews.json`、实验五的 `clean_data.csv`、`selling_points.csv`、`scores.csv`。审查 30 条评论和 13 条竞品耳机商品标题；一条非耳机配件被排除并记录。`用户重要度=主题提及评论数/30×100`；`标题覆盖率=命中标题数/13×100`；`机会分数=用户重要度×(1−标题覆盖率/100)`。至少 3 条评论提及且标题覆盖率不高于 25% 才生成机会。详细公式见 `docs/score_formula.md`。

标题词覆盖**不是**竞品所有营销内容的覆盖率；定向评论样本也不能代表市场总体。口味 0/30、标题 0/13，明确排除为伪机会。内容方向只是待验证的计划，不能宣称虚构品牌已经解决评论里的问题。来源与边界见 `docs/source_record.md`。

## 交付与检查

`outputs/theme_matrix.csv`、`outputs/opportunity_scores.csv`、`outputs/evidence_record.csv`、`outputs/strategy_briefs.json` 可重算。可读 Brief 见 `docs/strategy_briefs.md`，正反例见 `skills/brand-voice/references/examples.md`。Brand Voice 可由其他模块调用：`from src.brand_voice import validate_text, validate_brief`。

```powershell
python -m unittest discover -s tests -v
python tests\api_check.py
```

上传新编码 JSON 时填写来源与采集日期，原始文件独立留存在 `data/raw/uploads/`，结果写入 `outputs/runs/`；上传不会改动基准输入，也不会自动进行语义编码。

本项目实际调用 GitHub 原版 `skill-creator` 的 `quick_validate.py`，结果为 `Skill is valid!`；另保存原版 `brand-guidelines` 供结构参考，两者未改动。复验：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\brand-voice
```

`v0.6` 为课程版本标记，不使用 Git 标签。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.





