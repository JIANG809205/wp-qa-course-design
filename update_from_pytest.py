# -*- coding: utf-8 -*-
"""把 pytest 结果回填到用例工作簿，并刷新统计。"""

import json
import os

import openpyxl
from openpyxl.styles import Font, PatternFill

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "05-测试用例-核心40条.xlsx")
RESULTS = os.path.join(BASE, "wp-api-tests", "results.json")
TODAY = "2026-11-24"

results = json.load(open(RESULTS, encoding="utf-8"))
by_case = {r["case"]: r for r in results if r.get("case")}

wb = openpyxl.load_workbook(XLSX)
ws = wb["测试用例"]
heads = [c.value for c in ws[1]]
idx = {n: i + 1 for i, n in enumerate(heads)}

green = PatternFill("solid", fgColor="C6EFCE")
wrap_font = Font(name="微软雅黑", size=10)

filled = 0
for row in range(2, ws.max_row + 1):
    cid = ws.cell(row=row, column=idx["用例ID"]).value
    r = by_case.get(cid)
    if not r:
        continue
    ok = r["outcome"] == "passed"
    ws.cell(row=row, column=idx["执行结果"], value="通过" if ok else "失败")
    if ok:
        ws.cell(row=row, column=idx["执行结果"]).fill = green
    ws.cell(row=row, column=idx["实际结果"],
            value=f"接口自动化{'通过' if ok else '失败'}（pytest: {r['nodeid'].split('::')[-1]}）")
    ws.cell(row=row, column=idx["执行人"], value="接口自动化：pytest")
    ws.cell(row=row, column=idx["执行日期"], value=TODAY)
    filled += 1

# 统计
dist = {}
for row in range(2, ws.max_row + 1):
    v = ws.cell(row=row, column=idx["执行结果"]).value or "未执行"
    dist[v] = dist.get(v, 0) + 1

# 刷新汇总页
if "执行汇总" in wb.sheetnames:
    del wb["执行汇总"]
s = wb.create_sheet("执行汇总")
s.append(["统计项", "数值"])
total = ws.max_row - 1
executed = dist.get("通过", 0) + dist.get("失败", 0) + dist.get("阻塞", 0)
s.append(["用例总数", total])
s.append(["已执行", executed])
s.append(["执行率", f"{executed / total * 100:.1f}%"])
s.append(["通过", dist.get("通过", 0)])
s.append(["失败", dist.get("失败", 0)])
s.append(["未执行", dist.get("未执行", 0)])
s.append(["通过率（按已执行）", f"{dist.get('通过', 0) / executed * 100:.1f}%" if executed else "-"])
s.append(["自动化覆盖", "Selenium 9 条 + pytest 23 条"])
s.append(["更新日期", TODAY])
for i, w in enumerate([26, 26], start=1):
    s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for cell in s[1]:
    cell.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")

wb.save(XLSX)
print(f"回填 {filled} 条；执行结果分布: {dist}")
print(f"执行率: {executed / total * 100:.1f}%")
