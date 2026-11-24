# -*- coding: utf-8 -*-
"""把被插到"表头之后"的表标题移到表头之前。"""

import io
import re

MD = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
lines = io.open(MD, encoding="utf-8").read().splitlines()

SEP = re.compile(r"^\|[\s:\-|]+\|$")
CAP = re.compile(r"^表\s*\d+\.\d+")

moved = 0
for i in range(len(lines)):
    if not CAP.match(lines[i].strip()):
        continue
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines) or not SEP.match(lines[j].strip()):
        continue
    k = i - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if k < 0 or not lines[k].strip().startswith("|"):
        continue
    header = lines[k]
    lines[k] = lines[i].strip()
    lines[i] = header
    moved += 1

io.open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("已移动表标题:", moved, "处")

# 校验：标题后应紧跟表头，表头后紧跟分隔行
bad = 0
for i in range(len(lines)):
    if CAP.match(lines[i].strip()):
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and SEP.match(lines[j].strip()):
            bad += 1
print("仍错位的表标题:", bad)
