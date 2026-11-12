# GitHub 上传说明

`skills/webapp-testing/browsers/` 是 Playwright 本地浏览器运行时，包含超过 100 MB 的 `chrome-headless-shell.exe`，不提交到 GitHub。Skill 说明和 `scripts/with_server.py` 已保留。

需要执行浏览器验收时，在本机安装依赖并下载浏览器：

```powershell
python -m pip install playwright
python -m playwright install chromium
```

普通单元测试不依赖该浏览器运行时。
