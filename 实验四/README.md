# 实验四：消费者洞察引擎 v0.4

个人作业。项目把真实耳机评论、AI 语义标注、pandas 统计、Dashboard 与原评论 ID 证据查看串联起来。实验一、实验二、实验三目录未被读取或修改；实验三的 `clean_data.csv` 已在本项目内从同一固定公开源精确复现，哈希匹配。

## 启动

需要 Python 3.10+ 和 pandas 2.x–3.x。当前项目已验证 pandas 3.0.6。

```powershell
cd "$HOME\Desktop\实验四"
python src\consumer_insight_engine.py
python app.py
```

浏览器打开 `http://127.0.0.1:8504`。页面显示痛点排行、情绪分布、品牌对比、商品抓取日期和原评论 ID 证据；可下载编码 JSON。退出时按 `Ctrl+C`。

## 输入与复算

主输入是 `data/raw/reviews.csv`、`data/processed/semantic_annotations.json` 和 `data/processed/clean_data.csv`。`python src\consumer_insight_engine.py` 用 pandas 重算并生成 `outputs/encoded_reviews.json`、痛点与情绪统计表、品牌对比、证据索引及摘要。AI 编码文件不含统计值；`src/consumer_insight_engine.py` 不产生语义标签。百分比表均列出分母和样本量。一条评论可有多个痛点。

上传新数据时须同时提供评论 CSV 和已完成的 AI 编码 JSON；页面不会自动生成语义编码。可先用 `data/sample/case_normal.csv` 和 `data/sample/case_normal_codes.json` 试用。上传原始字节保存在 `data/raw/uploads/`，运行结果另存，不覆盖主数据。

## 验收

```powershell
python -m unittest discover -s tests -v
python tests\api_check.py
```

10 条内部编码核对见 `docs/audit_10.md`。**独立人工一致率尚未取得**，不能把内部 10/10 代替正式目标。源数据许可与局限见 `docs/source_and_ethics.md`；Prompt 见 `docs/prompt.md`；统计与证据见 `docs/insight_report.md`；AI 的事实、推断和建议见 `docs/ai_explanation.md`。

原版 GitHub `skill-creator` 保存在 `skills/github-skill-creator/`，实际运行其校验脚本确认本项目 Skill 有效。复验命令：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\consumer-insight (GitHub)
```

`v0.4` 为课程版本标记。评论时间全部缺失，页面中的时间表只代表商品列表抓取时间；两个公开数据源没有逐商品连接键。样本是定向选择，不能推断市场总体。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.


