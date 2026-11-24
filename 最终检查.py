# -*- coding: utf-8 -*-
"""最终一致性检查：用例表、缺陷表、关键产物是否存在。"""

import os

import openpyxl

XLSX = r"E:\软件质量保证与测试课程设计\05-测试用例-核心40条.xlsx"
wb = openpyxl.load_workbook(XLSX)
ws = wb["测试用例"]
dist = {}
for r in range(2, ws.max_row + 1):
    v = ws.cell(row=r, column=10).value or "未执行"
    dist[v] = dist.get(v, 0) + 1
print("用例:", ws.max_row - 1, dist)
print("缺陷记录:", wb["缺陷记录"].max_row - 1)

ARTS = {
    "严格合规(Flash 3轮)": r"E:\软件质量保证与测试课程设计\llm-qa\outputs\rigor\summary-deepseek-v4.1-flash.json",
    "triage24": r"/opt/qa/rigor-triage/triage24-summary.json",
    "scripts10": r"E:\软件质量保证与测试课程设计\llm-qa\outputs\scripts10\scripts10-summary.json",
    "cost": r"E:\软件质量保证与测试课程设计\llm-qa\outputs\cost-estimate.json",
    "compat": r"E:\软件质量保证与测试课程设计\wp-compat\compat.json",
    "versions": r"E:\软件质量保证与测试课程设计\defect-hunt\findings-versions.json",
    "perf-rigor": r"E:\软件质量保证与测试课程设计\wp-perf\results-rigor",
    "perf-list": r"E:\软件质量保证与测试课程设计\wp-perf\results-rigor-list",
    "matrix-reps": r"E:\软件质量保证与测试课程设计\defect-hunt\matrix-reps",
    "ci": r"E:\软件质量保证与测试课程设计\.github\workflows\ci.yml",
}
for k, v in ARTS.items():
    print(f"  {k:<20} {'存在' if os.path.exists(v) else '缺失'}")
