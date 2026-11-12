# 实验三：营销数据获取与清洗

**作业形式：**个人作业  
**版本：**v0.3  
**完成日期：**2026-11-10

## 第 5 周

从品牌定价与评分的竞争问题反推字段。比较静态 HTML、公开 API 和教师数据集三种方式，记录于 `docs/method_comparison.md`。选定有非商业教育研究许可的公开快照，记录来源、日期、固定版本和 SHA-256，见 `docs/source_record.md`。建立数据字典、伦理检查表，并将前 50 条写入 `data/sample/first_50.csv`。

## 第 6 周

使用 `src/collect.py` 固定抽取 480 条，保留 `data/raw/raw_data.csv`；使用 `src/clean.py` 输出 `data/processed/clean_data.csv`。处理 69 条重复编号，规范化 52 条品牌别名，标记保留 5 条价格异常；有效日期转为日期字段，关注数缺失保持空白。最终 411 条、总体分析字段完整率 95.47%。日志和统计保存在 `outputs/`。

## 接回上传流程

`app.py` 延续前期本地上传的输入元数据、字段校验、原始字节独立存储、处理结果分层存储逻辑。页面支持上传同结构 CSV 并查看质量统计和前 10 条结果。上传主样本、50 条样本以及缺字段请求均已通过端到端检查。项目实现独立完成，不读取或修改前两个实验目录。

## GitHub Skill 使用

从 GitHub [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) 获取指南与 `quick_validate.py`，在项目内编写 `skills/data-validation (GitHub)/SKILL.md` 并实际运行 GitHub 脚本校验，输出 `Skill is valid!`。管线运行时执行本地确定性脚本，不使用大模型 API。

## 验收结果

| 标准 | 本次证据 |
|---|---|
| 来源可追溯 | 来源 URL、许可、commit、blob、源文件与抽取文件哈希俱全 |
| 字段完整率至少 90% | 八个分析字段总体 95.47%，统计可由 CSV 重新计算 |
| 原始数据保留 | `raw_data.csv` 独占新建；清洗前校验哈希；重复清洗后哈希不变 |
| 清洗可重复 | 再运行输出与已有 `clean_data.csv` 字节一致 |
| 无敏感字段 | 卖家用户名、位置及联系方式未导入；只保留商品与汇总互动字段 |
| 删除、修改、保留规则可解释 | `docs/cleaning_rules.md` 和 `outputs/cleaning_log.json` |
| 统计与抽查一致 | 5 项单元测试通过；两个固定编号的价格、评分、评论数、日期、关注数核对一致 |

数据集为非随机且经过完整字段筛选的子集，不能据此推断市场总体。评论正文和评论时间均不可用，不应据此声称完成消费者评论分析。

