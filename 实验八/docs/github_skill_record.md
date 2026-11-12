# GitHub 现成 Skill 接入记录

GitHub 来源：`https://github.com/openai/skills/tree/main/skills/.system/skill-creator`。本项目 `skills/github_skill_creator/SKILL.md` 是该仓库原版副本；`quick_validate.py` 增加了项目根目录路径校验，拒绝检查实验八以外的文件。该 Skill 用于检查本项目复制接入的 `skills/brand-voice` 与 `skills/consumer-insight` 的 frontmatter 和目录结构。

执行命令：

```powershell
$env:PYTHONUTF8='1'
.\.venv\Scripts\python.exe skills/github_skill_creator/quick_validate.py skills/brand-voice
.\.venv\Scripts\python.exe skills/github_skill_creator/quick_validate.py skills/consumer-insight
```

两项输出均为 `Skill is valid!`。`PYTHONUTF8=1` 解决 Windows 默认 GBK 解码问题。此 GitHub Skill 是项目内开发和校验工具；运行页面实际调用前序实验 Skill 对应的 Python 能力。GitHub 源码接入不代表调用大模型 API。


