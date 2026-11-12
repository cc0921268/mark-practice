# 测试与个人验收记录

日期：2026-11-10  
版本：v0.1  
执行者：个人自测

## 自动测试

命令：`python -m unittest discover -s tests -v`  
结果：4 项通过，0 项失败。

浏览器验收使用项目内 GitHub `webapp-testing` Skill 的 `with_server.py` 启动本地服务，再执行 `tests/browser_check.py`。结果：`Browser acceptance: normal upload, chart/table, filter, missing field, empty values OK`。截图：`outputs/running_screenshot.png`。

## 三类 CSV 与预期、实测

| 文件 | 预期 | 实测 | 结论 |
|---|---|---|---|
| `data/sample/normal.csv` | 4 条有效；星河价格 150.00、评分 4.50；青竹价格 100.00、评分 4.00 | 与预期一致；双柱状图和表格均显示 2 个品牌 | 通过 |
| `data/sample/missing_field.csv` | 明确提示缺少 `rating` | 页面显示“CSV 缺少必需字段：rating” | 通过 |
| `data/sample/empty_values.csv` | 2 条有效、3 条跳过；显示行号 | 与预期一致；提示第 3、4、5 行 | 通过 |

## 验收标准逐项核对

| 标准 | 证据 | 结论 |
|---|---|---|
| 按 README 启动 | Skill 辅助脚本调用 `python app.py`，8501 端口就绪，浏览器打开首页 | 通过 |
| 均值与手工抽查一致 | `(100+200)/2=150.00`，`(4.0+5.0)/2=4.50`；单元测试与页面结果一致 | 通过 |
| 缺字段明确提示 | 缺字段样例提示 `rating` 字段名 | 通过 |
| 筛选不修改原始数据 | 筛选为“星河”时表格 1 行，切回全部后 2 行；三份上传原始文件 SHA-256 均与处理日志记录一致 | 通过 |
| 可独立上传查看结果 | 浏览器脚本从打开首页开始，独立完成上传、图表与表格检查 | 通过 |
| 结果保留 | 程序、样例、文档、原始上传、分析 JSON、日志和截图均位于项目目录 | 通过 |

本记录是个人自测；教师或同学可依 README 重复验收。教师原始 `marketing_data.csv` 尚未提供，因此未对其内容进行实测。
