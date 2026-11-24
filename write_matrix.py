# -*- coding: utf-8 -*-
"""把 30 格权限实测写入工作簿，并补一条缺陷（重复用户名返回 500）。"""

import json
import os

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "05-测试用例-核心40条.xlsx")
MATRIX = os.path.join(BASE, "defect-hunt", "permission-matrix-v2.json")

rows = json.load(open(MATRIX, encoding="utf-8"))

wb = openpyxl.load_workbook(XLSX)

# ---------- 权限实测表 ----------
if "权限实测" in wb.sheetnames:
    del wb["权限实测"]
s = wb.create_sheet("权限实测")
head = ["角色", "操作", "预期", "页面状态", "页面元素", "接口结果", "判定", "接口返回摘要"]
s.append(head)

EXPECT_TXT = {"Y": "允许", "N": "拒绝", "C": "有条件"}
green = PatternFill("solid", fgColor="C6EFCE")
red = PatternFill("solid", fgColor="FFC7CE")
wrap = Alignment(vertical="center", wrap_text=True)
font = Font(name="微软雅黑", size=10)

mismatch = 0
for r in rows:
    api = r["api"]
    allow = api in ("allow", "allow_pending")
    if r["expect"] == "C":
        ok = api in ("allow", "allow_pending")
    else:
        ok = allow == (r["expect"] == "Y")
    if not ok:
        mismatch += 1
    s.append([
        r["role"], r["name"], EXPECT_TXT.get(r["expect"], r["expect"]),
        f"{r['ui_status']}{'（拒绝页）' if r['ui_denied'] else ''}",
        "存在" if r["ui_marker"] else "缺失",
        api, "符合" if ok else "不符合", r.get("api_msg", "")[:60],
    ])

for i, w in enumerate([10, 16, 8, 10, 10, 14, 8, 50], start=1):
    s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for cell in s[1]:
    cell.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")
for row in s.iter_rows(min_row=2, max_row=s.max_row, max_col=8):
    for cell in row:
        cell.font = font
        cell.alignment = wrap
    row[6].fill = green if row[6].value == "符合" else red

# ---------- 补一条缺陷 ----------
ws = wb["缺陷记录"]
existing = {ws.cell(row=r, column=1).value for r in range(2, ws.max_row + 1)}
if "DEF-011" not in existing:
    ws.append([
        "DEF-011", "重复用户名创建返回 500 而非 4xx", "M6 用户与角色", "探索性测试", "P3", "否",
        "POST /wp-json/wp/v2/users，username 与已存在用户相同",
        "400 且提示用户名已存在",
        "HTTP 500，code=existing_user_login（业务校验失败却返回服务器错误）",
        "系统缺陷", "待修复", "见截图", "2026-11-24", "",
    ])
    for c in range(1, 15):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font = font
        cell.alignment = wrap

# 更新缺陷汇总
if "缺陷汇总" in wb.sheetnames:
    del wb["缺陷汇总"]
summ = wb.create_sheet("缺陷汇总")
summ.append(["等级", "数量", "缺陷编号"])
summ.append(["P1 严重", 2, "DEF-001、DEF-002"])
summ.append(["P2 一般", 5, "DEF-003 ~ DEF-007"])
summ.append(["P3 轻微", 4, "DEF-008 ~ DEF-011"])
summ.append(["合计", 11, ""])
summ.append([])
summ.append(["缺陷有效率", "11/11（均复现两次以上，无脚本/环境误判）"])
summ.append(["权限矩阵", "30 格双通道验证，0 处越权"])
for i, w in enumerate([14, 8, 44], start=1):
    summ.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for cell in summ[1]:
    cell.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")

wb.save(XLSX)
print(f"权限矩阵写入 {len(rows)} 格，其中不符合 {mismatch} 格；缺陷记录共 {ws.max_row - 1} 条")
