# -*- coding: utf-8 -*-
"""修正工作簿：3 条兼容性用例的需求ID与模块名。"""

import openpyxl
from openpyxl.styles import Alignment, Font

P = r"E:\软件质量保证与测试课程设计\05-测试用例-核心40条.xlsx"
wb = openpyxl.load_workbook(P)
ws = wb["测试用例"]
heads = [c.value for c in ws[1]]
idx = {n: i + 1 for i, n in enumerate(heads)}

fixed = 0
for r in range(2, ws.max_row + 1):
    cid = str(ws.cell(row=r, column=idx["用例ID"]).value or "")
    if cid.startswith("TC-COMP"):
        ws.cell(row=r, column=idx["模块"], value="兼容性")
        ws.cell(row=r, column=idx["需求ID"], value="R11")
        fixed += 1

# 在执行汇总页追加基线说明
if "执行汇总" in wb.sheetnames:
    s = wb["执行汇总"]
    row = s.max_row + 2
    s.cell(row=row, column=1, value="数据基线").font = Font(name="微软雅黑", size=10, bold=True)
    s.cell(row=row, column=2,
           value="1000 篇文章 / 20000 条评论 / 6 个角色账号（测试残留已清理）").alignment = Alignment(wrap_text=True)

wb.save(P)
print("已修正兼容性用例:", fixed, "条")
for r in range(2, ws.max_row + 1):
    cid = str(ws.cell(row=r, column=idx["用例ID"]).value or "")
    if cid.startswith("TC-COMP"):
        print("  ", cid, ws.cell(row=r, column=idx["模块"]).value,
              ws.cell(row=r, column=idx["需求ID"]).value)
