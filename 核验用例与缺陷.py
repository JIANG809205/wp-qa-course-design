# -*- coding: utf-8 -*-
"""核验报告中的关键数字：用例优先级分布、缺陷编号对应、追溯完整性。"""

from __future__ import annotations

import collections
import os
import re

import openpyxl

ROOT = r"E:\软件质量保证与测试课程设计"
XLSX = os.path.join(ROOT, "05-测试用例-核心40条.xlsx")

wb = openpyxl.load_workbook(XLSX)
print("工作表:", wb.sheetnames)
ws = wb["测试用例"]
heads = [c.value for c in ws[1]]
idx = {n: i + 1 for i, n in enumerate(heads)}
print("列:", heads)

rows = []
for r in range(2, ws.max_row + 1):
    rows.append({n: ws.cell(row=r, column=i).value for n, i in idx.items()})

print(f"\n用例总数: {len(rows)}")

prio = collections.Counter(str(x.get("优先级", "")).strip() for x in rows)
print("优先级分布:", dict(prio))

res = collections.Counter(str(x.get("执行结果", "") or "未执行").strip() for x in rows)
print("执行结果:", dict(res))

for p in ("P0", "P1", "P2"):
    sub = [x for x in rows if str(x.get("优先级", "")).strip() == p]
    ok = sum(1 for x in sub if str(x.get("执行结果", "")).strip() == "通过")
    print(f"  {p}: {ok}/{len(sub)} = {ok/len(sub)*100:.1f}%" if sub else f"  {p}: 无")

print("\n按需求 ID 统计:")
c = collections.Counter(str(x.get("需求ID", "") or "无").strip() for x in rows)
for k in sorted(c):
    print(f"  {k}: {c[k]}")

print("\n模块分布:")
m = collections.Counter(str(x.get("模块", "") or "无").strip() for x in rows)
for k, v in m.items():
    print(f"  {k}: {v}")

# 缺陷编号检查
ws2 = wb["缺陷记录"]
dh = [c.value for c in ws2[1]]
didx = {n: i + 1 for i, n in enumerate(dh)}
print("\n缺陷记录编号与等级:")
for r in range(2, ws2.max_row + 1):
    print("  ", ws2.cell(row=r, column=1).value, ws2.cell(row=r, column=didx.get("严重等级", 5)).value,
          str(ws2.cell(row=r, column=didx.get("缺陷标题", 2)).value)[:30])

# 报告中的缺陷编号引用是否一致
md = open(os.path.join(ROOT, "报告-按示例模板.md"), encoding="utf-8").read()
print("\n报告里 DEF 编号出现次数:")
for k, v in sorted(collections.Counter(re.findall(r"DEF-\d{3}", md)).items()):
    print(f"  {k}: {v}")
