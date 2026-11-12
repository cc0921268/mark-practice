# 营销数据分析工具 v0.1

个人实验作业。上传 CSV 后按品牌显示平均价格、平均评分、柱状图，并可筛选品牌。程序只在本机运行，不调用大模型 API。

## 启动

需要 Python 3.10 或更新版本。项目运行不需要安装第三方依赖。

```powershell
cd "$HOME\Desktop\实验一"
python app.py
```

浏览器打开 `http://127.0.0.1:8501`。退出时在运行窗口按 `Ctrl+C`。如 8501 端口已占用，可先设置环境变量 `MARKETING_OS_PORT` 为其他端口，再运行 `python app.py`。

## 使用

1. 选择 UTF-8 编码的 CSV，建议先试 `data/sample/normal.csv`。
2. 填写数据来源和采集日期，点击“上传并分析”。
3. 查看两个柱状图与品牌汇总表，使用“按品牌筛选”切换品牌。

必需字段为 `brand`、`price`、`rating`；`product`、`sales` 可有可无。缺少必需字段会显示字段名。必需值为空或不是有效数字的行会跳过，并显示行号；若全部跳过，则显示错误。计算使用未加权算术平均，最终保留两位小数。例：`normal.csv` 中星河价格 `(100+200)/2=150.00`、评分 `(4.0+5.0)/2=4.50`。

上传文件最大 5 MB。原始上传文件只追加保存到 `data/raw/`；分析结果存于 `data/processed/`，处理日志存于 `outputs/processing_log.jsonl`。品牌筛选只改变页面展示，不会修改上述文件。仅上传公开、结构清晰且允许访问的数据，不上传个人敏感信息。

## 测试

```powershell
python -m unittest discover -s tests -v
```

三套测试文件在 `data/sample/`：`normal.csv`、`missing_field.csv`、`empty_values.csv`。测试结果见 `docs/test_record.md`，问题定位见 `docs/debug_log.md`，运行截图见 `outputs/`。实验说明和需求卡见 `docs/experiment01.md`，需求 Prompt 见 `docs/requirements_prompt.md`。

教师的 `marketing_data.csv` 未提供给本项目，拿到后直接通过页面上传；请填写真实来源及采集日期。`v0.1` 是课程交付版本标记，本项目不使用 Git。
