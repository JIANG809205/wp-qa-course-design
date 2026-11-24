# -*- coding: utf-8 -*-
"""更新项目审查报告中已完成/待办的状态。"""

import io
import os

p = r"E:\软件质量保证与测试课程设计\项目审查报告.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("| 待完成 | 2 | 报告正文 8 章、Pro 模型 20 条脚本（进行中） |",
              "| 待完成 | 1 | 报告正文 8 章 |")

t = t.replace("- **已完成**：DeepSeek-V4.1-Flash 13/20 = 65.0%（CI 43%–82%）；Qwen-Plus 0/20（CI 0%–16%）。\n- **进行中**：DeepSeek-V4-Pro（推理耗时约 90 秒/次）。",
              "- **结果（n=20，Wilson 95% CI）**：DeepSeek-V4.1-Flash 13/20 = **65.0% [43%, 82%]**；"
              "DeepSeek-V4-Pro 0/20 = **0% [0%, 16%]**；Qwen-Plus 0/20 = **0% [0%, 16%]**。")

t = t.replace("| 大模型-脚本 | n=20（Flash 65%、Qwen 0%，Pro 进行中） | ⏳ |",
              "| 大模型-脚本 | n=20：Flash 65%、Pro 0%、Qwen 0%（均带 Wilson CI） | ✅ |")

t = t.replace("| 1 | 定位器保真度只统计 `By.id` / `By.name` / CSS 中的 `#id` | 不含 class、XPath、文本定位，可能低估实际可用性 | 报告中写明口径 |",
              "| 1 | ~~定位器基准不完整~~ | 已修正：改为从 9 个真实页面抓取 1181 id / 193 name / 769 class 作为基准，并计入 CSS 与 XPath | ✅ 已修复（保真度因此从 52% 回落到 21%） |")

t = t.replace("1. **等 Pro 的 20 条脚本跑完**，把三模型 n=20 数据统一写入第 6 章与结果分析；\n",
              "")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("审查报告已更新")
for line in t.splitlines():
    if "待完成" in line or "大模型-脚本" in line:
        print(" ", line)
