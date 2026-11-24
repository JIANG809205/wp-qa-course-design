# llm-qa · 大模型测试助手

把 DeepSeek 接进测试流程的四个环节，并量化它的实际效果。

## 一、四个环节

| 任务 | 输入 | 输出 | 度量指标 |
|---|---|---|---|
| `cases` 需求→用例 | 功能点 + UI 定位 + 角色 | JSON 用例数组 | 合法 JSON 率、字段完整率、与人工用例重合率、新增用例数 |
| `scripts` 用例→脚本 | 单条用例 | Selenium+TestNG Java 方法 | 语法/结构校验通过率、含断言率、含显式等待率 |
| `triage` 日志→归因 | 失败日志 | `{category, reason, evidence_needed}` | 与人工标注一致率、**把非缺陷误判为缺陷的次数** |
| `report` 数据→分析 | 压测汇总 | 中文分析段落 | 字数、人工修改比例（人工填） |

## 二、三种后端

| provider | 说明 | 需要什么 |
|---|---|---|
| `deepseek` | 官方 OpenAI 兼容接口 | `DEEPSEEK_API_KEY` |
| `ollama` | 本地模型，离线可复现 | 本机 11434 端口 |
| `mock` | 不联网占位，用于验证流水线 | 无 |

## 三、配置

复制 `.env` 并填入真实 key（该文件已在 `.gitignore` 中，不要提交）：

```
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 四、运行

```bash
cd llm-qa
/opt/qa-venv/bin/python run.py --provider mock --task all          # 验证流水线
/opt/qa-venv/bin/python run.py --provider deepseek --task all      # 真实调用
/opt/qa-venv/bin/python run.py --provider deepseek --model deepseek-reasoner --task all
```

输出目录 `outputs/<provider>-<时间戳>/`，内含：

```
cases/   每个功能点一份原始 JSON + summary.json
scripts/ 生成的 Java 方法 + summary.json
triage/  每条日志的判定 + summary.json
report/  perf-analysis.md
metrics.json  本次运行的汇总指标
```

## 五、设计要点（写进报告的部分）

1. **强制结构化输出**：提示词要求“只输出 JSON 数组、不要代码块”，解析端仍做兜底（剥 ``` 围栏、正则截取），统计“合法 JSON 率”而不是假设它一定合法。
2. **不做无根据判定**：归因提示词明确“证据不足时不要臆断为系统缺陷”，并单独统计“把非缺陷误判为缺陷”的次数——这是最危险的一类错误，直接关系到会不会给被测系统乱扣缺陷。
3. **可复现**：`temperature=0.2` 固定、输入数据集固定、输出全部落盘，换模型只需改一个参数。
4. **人机分工**：模型只产出候选，采纳与否由人工标记（`human_overlap_rate` 与报告里的人工复核记录）。

## 六、当前状态

- 流水线已用 `mock` 后端跑通：6 个功能点 → 12 条用例、3 个脚本、5 条日志归因、1 段分析，全流程无报错。
- 真实模型调用待 API key 就绪（当前提供的 `sk-ws-` 前缀 key 对 `api.deepseek.com` 返回 401）。
