# 实验三：蓝牙耳机营销数据获取与清洗 v0.3

个人作业。公开耳机商品列表经固定版本导入、去重和标准化，生成可复现的分析数据。项目不调用大模型 API；实验一、实验二文件未被读取或修改。

## 已交付数据

- `data/raw/raw_data.csv`：480 条未清洗的抽取记录，脚本拒绝覆盖。
- `data/sample/first_50.csv`：第 5 周字段检查用的前 50 条。
- `data/processed/clean_data.csv`：411 条清洗结果，8 个分析字段总体完整率 95.47%。
- `outputs/collection_log.json`、`outputs/cleaning_log.json`、`outputs/quality_statistics.json`：来源哈希、变更数量和质量统计。

公开来源与许可见 `docs/source_record.md`；字段见 `docs/data_dictionary.md`；逐类处理规则见 `docs/cleaning_rules.md`。源数据没有评论原文，只含评论数量和关注数量；`wireless_flag_proxy` 记录是无线耳机代理样本，不能据此确认具体蓝牙协议。

## 运行与复现

需要 Python 3.10 或更新版本；主程序只使用标准库。

```powershell
cd "$HOME\Desktop\实验三"
python src\clean.py
python app.py
```

浏览器访问 `http://127.0.0.1:8503`，查看统计或下载清洗结果。上传 `data/sample/first_50.csv`、填写来源与采集日期，可验证同结构 CSV 清洗流程；上传原始字节另存至 `data/raw/uploads/`，不会覆盖主数据集。退出时按 `Ctrl+C`。

`python src\clean.py` 可重复运行，输出内容哈希保持相同。`src/collect.py` 是固定源文件的导入脚本；只有在 `raw_data.csv` 和 50 条样本均不存在时才能运行，避免原始数据被覆盖。重新导入需使用独立空目录并遵守数据许可；当前交付已保留原始文件，无需再采集。

## 验收

```powershell
python -m unittest discover -s tests -v
python tests\api_check.py
```

GitHub 现有 `skill-creator` 已保存于 `skills/github-skill-creator/`，并实际调用其 `quick_validate.py` 验证本项目的 `skills/data-validation (GitHub)/SKILL.md`，结果为 `Skill is valid!`。重复验证：

```powershell
$env:PYTHONPATH = (Resolve-Path 'skills\github-skill-creator\vendor').Path
$env:PYTHONUTF8 = '1'
python skills\github-skill-creator\scripts\quick_validate.py skills\data-validation (GitHub)
```

项目版本标记为 **v0.3**，不依赖 Git 标签。

## Skill compliance (updated 2026-11-12)
Former project-authored business Skill folders were removed. GitHub source and adaptation records are in docs/skill_compliance.md and skills/*/ADAPTATION.md. No new business Skill is defined here.


