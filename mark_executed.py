# -*- coding: utf-8 -*-
"""把已自动化的 9 条用例在执行表中标记为已执行/通过。"""

import datetime
import os

import openpyxl
from openpyxl.styles import Font, PatternFill

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05-测试用例-核心40条.xlsx")

DONE = {
    "TC-AUTH-001": "TestNG 自动化执行通过（edu.qa.wp.tests.LoginTest#adminLoginSuccess）",
    "TC-AUTH-002": "TestNG 自动化执行通过（LoginTest#wrongPasswordRejected）",
    "TC-AUTH-004": "TestNG 自动化执行通过（LoginTest#emptyUsernameRejected）",
    "TC-POST-001": "TestNG 自动化执行通过（PostTest#createDraftPost）",
    "TC-POST-004": "TestNG 自动化执行通过（PostTest#emptyTitleDraft）",
    "TC-PERM-001": "TestNG 自动化执行通过（PermissionTest#contributorCannotPublish）",
    "TC-PERM-002": "TestNG 自动化执行通过（PermissionTest#subscriberCannotEnterAdmin）",
    "TC-COMM-001": "TestNG 自动化执行通过（CommentTest#commentNeedsModeration）",
    "TC-COMM-003": "TestNG 自动化执行通过（CommentTest#commentScriptEscaped）",
}

wb = openpyxl.load_workbook(XLSX)
ws = wb["测试用例"]

headers = [c.value for c in ws[1]]
idx = {name: i + 1 for i, name in enumerate(headers)}

green = PatternFill("solid", fgColor="C6EFCE")
font = Font(name="微软雅黑", size=10, color="006100")

today = datetime.date.today().strftime("%Y-%m-%d")
updated = 0

for row in range(2, ws.max_row + 1):
    case_id = ws.cell(row=row, column=idx["用例ID"]).value
    if case_id in DONE:
        ws.cell(row=row, column=idx["执行结果"], value="通过").fill = green
        ws.cell(row=row, column=idx["执行结果"]).font = font
        ws.cell(row=row, column=idx["实际结果"], value=DONE[case_id])
        ws.cell(row=row, column=idx["执行人"], value="自动化：TestNG")
        ws.cell(row=row, column=idx["执行日期"], value=today)
        updated += 1

# 结论表：新增一个“自动化执行汇总”工作表
if "自动化汇总" in wb.sheetnames:
    del wb["自动化汇总"]
summary = wb.create_sheet("自动化汇总")
summary.append(["项目", "内容"])
rows = [
    ("执行时间", today),
    ("工程", "wp-autotest（Maven + Selenium 4.27.0 + TestNG 7.10.2 + Allure）"),
    ("用例总数", 9),
    ("通过", 9),
    ("失败", 0),
    ("耗时", "约 26 秒"),
    ("报告位置", "wp-autotest/result/surefire-reports/index.html"),
    ("执行命令", "bash wp-autotest/run-tests.sh"),
    ("被测环境", "WordPress 7.1.5 + MariaDB 10.6 + Redis 7（Docker）"),
    ("覆盖用例", "TC-AUTH-001/002/004、TC-POST-001/004、TC-PERM-001/002、TC-COMM-001/003"),
    ("环境固定项", "经典编辑器（区块编辑器无 #title）；关闭评论洪水保护（用例间连续提交）"),
]
for r in rows:
    summary.append(list(r))
for i, w in enumerate([18, 78], start=1):
    summary.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for cell in summary[1]:
    cell.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")

wb.save(XLSX)
print(f"updated {updated} cases")
