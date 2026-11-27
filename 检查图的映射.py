# -*- coding: utf-8 -*-
"""校验报告中所有图标记是否都能在生成脚本里找到、且文件存在。"""

import io
import os
import re

ROOT = r"E:\软件质量保证与测试课程设计"
GEN = os.path.join(ROOT, "生成报告docx-模板.py")
MD = os.path.join(ROOT, "报告-按示例模板.md")

gen = io.open(GEN, encoding="utf-8").read()
md = io.open(MD, encoding="utf-8").read()

fig_block = re.search(r"FIG = \{(.*?)\n\}", gen, re.S).group(1)
mapping = dict(re.findall(r'"([A-Za-z0-9\-]+)":\s*"([^"]+)"', fig_block))

used = re.findall(r"\[\[图:([A-Za-z0-9\-]+)\|", md)
print(f"报告中引用图 {len(set(used))} 个，脚本已登记 {len(mapping)} 个\n")

missing_map, missing_file = [], []
for k in dict.fromkeys(used):
    if k not in mapping:
        missing_map.append(k)
        continue
    p = os.path.join(ROOT, mapping[k].replace("/", os.sep))
    if not os.path.exists(p):
        missing_file.append((k, mapping[k]))

print("脚本缺少映射:", missing_map or "无")
print("映射了但文件不存在:", missing_file or "无")

# 输出可用图文件
print("\ncharts-final 现有图:")
for f in sorted(os.listdir(os.path.join(ROOT, "wp-perf", "charts-final"))):
    if f.endswith(".png"):
        print("  ", f)
