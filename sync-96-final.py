# -*- coding: utf-8 -*-
"""把 n=96 的最终数据写入第 6 章、结果分析、审计与核验文档。"""

import io
import os

ROOT = r"E:\软件质量保证与测试课程设计"

TABLE_NEW = """| 指标 | DeepSeek-V4.1-Flash | DeepSeek-V4-Pro | Qwen-Plus |
|---|---|---|---|
| 每轮生成用例数 | 198 | 196 | 196 |
| 严格结构合规率（用例） | **95.6% ± 8.0%**（3 轮） | 55.1%（1 轮） | 74.5%（1 轮） |
| 需求点覆盖率（用例） | 96.2% | 96.2% | 93.6% |
| 定位器保真度（n=96，真实 DOM） | **29.0%** | 33.1% | 34.9% |
| 有类声明的脚本 | 99% | 73% | 0% |
| URL 指向被测环境 | 65% | 1% | 4% |
| 结构可运行率（n=96） | **64.6%** [54.6%, 73.4%] | 1.0% [0.2%, 5.7%] | 0% [0%, 3.8%] |
| **严格可运行率（n=96）** | **5.2%** [2.2%, 11.6%] | 1.0% [0.2%, 5.7%] | 0% [0%, 3.8%] |
| 脚本编译通过率（早期 3 条样本） | 3/3 | 2/3 | 0/3 |
| 归因准确率（n=24） | **95.8%** | 91.7% | 91.7% |
| 误判为缺陷次数 | **0** | 0 | 0 |"""

OLD_TABLE_START = "| 指标 | DeepSeek-V4.1-Flash | DeepSeek-V4-Pro | Qwen-Plus |"
OLD_TABLE_END = "| 误判为缺陷次数 | **0** | 0 | 0 |"


def replace_block(text: str, start: str, end: str, new: str) -> str:
    i = text.find(start)
    if i < 0:
        return text
    j = text.find(end, i)
    if j < 0:
        return text
    j += len(end)
    return text[:i] + new + text[j:]


EDITS = [
    (r"06-报告章节-大模型使用过程及经验.md", "table6_3"),
    (r"llm-qa\结果分析.md", "table6_1"),
]

for rel, kind in EDITS:
    p = os.path.join(ROOT, rel)
    t = io.open(p, encoding="utf-8").read()
    before = t
    t = replace_block(t, OLD_TABLE_START, OLD_TABLE_END, TABLE_NEW)
    if t != before:
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        print("OK  表格已替换:", rel)
    else:
        print("MISS 未找到表格:", rel)

# 口径声明与结论
p = os.path.join(ROOT, r"06-报告章节-大模型使用过程及经验.md")
t = io.open(p, encoding="utf-8").read()
t = t.replace("> 2. 脚本类指标（有类声明 / URL / 可运行 / 定位器保真）：三模型均为 **20 条样本**，`n=20`，"
              "比例结论附 **Wilson 95% 置信区间**；定位器基准为真实 DOM（1181 id / 193 name / 769 class）。",
              "> 2. 脚本类指标（有类声明 / URL / 可运行 / 定位器保真）：三模型均为 **96 条样本**（脚本数 20 → 96），"
              "比例结论附 **Wilson 95% 置信区间**；定位器基准为真实 DOM（1181 id / 193 name / 769 class）。")
t = t.replace("1. **定位器保真度是所有模型的共同短板**：以真实 DOM（1181 id / 193 name / 769 class）为基准、20 条脚本为样本，"
              "三模型依次为 **21.1%、24.4%、25.0%**，即**四分之三以上的定位器是编造的**；这也直接决定了严格可运行率只有 5%。",
              "1. **定位器保真度是所有模型的共同短板**：以真实 DOM（1181 id / 193 name / 769 class）为基准、96 条脚本为样本，"
              "三模型依次为 **29.0%、33.1%、34.9%**，即**约七成定位器是编造的**；这直接决定了严格可运行率最高只有 5.2%。")
t = t.replace("2. **\"看起来对\"与\"跑得起来\"之间存在巨大鸿沟**：Flash 严格合规率 95.6%、结构可运行率 65%，"
              "但**严格可运行只有 1/20（5%）**——因为 13 个\"结构可运行\"脚本里，每一个都至少含一个虚构定位器，执行到那一步就会抛 `NoSuchElementException`。"
              "Pro 与 Qwen 的结构可运行率本身就是 0（Pro 18/20 有类声明但 20 条 URL 全错；Qwen 0/20 有类声明）。",
              "2. **\"看起来对\"与\"跑得起来\"之间存在巨大鸿沟**：Flash 严格合规率 95.6%、结构可运行率 64.6%，"
              "但**严格可运行只有 5/96（5.2%）**——因为结构合格的脚本里几乎每一个都含虚构定位器，执行到那一步就会抛 `NoSuchElementException`。"
              "Pro 的结构可运行率仅 1.0%（73% 有类声明，但 96 条里只有 1 条用对 URL）；Qwen 则 0% 有类声明。")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("OK  第 6 章口径与结论已更新")

# 评测方法依据
p2 = os.path.join(ROOT, r"llm-qa\评测方法依据.md")
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("据此重算后（样本 96 条脚本），DeepSeek-V4.1-Flash 的定位器保真度为 **29.0%**（644 个定位器中 187 个真实存在），"
                "即**约七成定位器在真实页面上不存在**；另两模型的 96 条评测仍在进行。",
                "据此重算后（样本 96 条脚本），三模型定位器保真度为 **29.0% / 33.1% / 34.9%**，"
                "即**约七成定位器在真实页面上不存在**。")
io.open(p2, "w", encoding="utf-8", newline="\n").write(t2)
print("OK  评测方法依据已更新")
