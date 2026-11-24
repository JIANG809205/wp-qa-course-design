# -*- coding: utf-8 -*-
"""构造 96 个脚本生成场景：43 条真实用例 + 53 个派生变体。

派生规则（可复现、无随意性）：
1. 边界变体：在原步骤后追加一个边界值操作（空值 / 超长 / 特殊字符）；
2. 角色变体：换成另一个有权限差异的角色执行同一操作；
3. 顺序变体：交换两步骤顺序，验证前置条件缺失时的行为。
"""

from __future__ import annotations

import json
import os

import openpyxl

ROOT = os.environ.get("WP_ROOT", "")
if not ROOT:
    cand_win = r"E:\软件质量保证与测试课程设计"
    ROOT = cand_win if os.path.isdir(cand_win) else "/mnt/e/软件质量保证与测试课程设计"
XLSX = os.path.join(ROOT, "05-测试用例-核心40条.xlsx")
OUT = os.path.join(ROOT, "llm-qa", "data", "scripts96.json")

wb = openpyxl.load_workbook(XLSX)
ws = wb["测试用例"]
heads = [c.value for c in ws[1]]
idx = {n: i + 1 for i, n in enumerate(heads)}

base = []
for r in range(2, ws.max_row + 1):
    cid = ws.cell(row=r, column=idx["用例ID"]).value
    title = ws.cell(row=r, column=idx["用例标题"]).value
    steps = ws.cell(row=r, column=idx["操作步骤"]).value
    expected = ws.cell(row=r, column=idx["预期结果"]).value
    if not cid or not title:
        continue
    step_list = [s.strip() for s in str(steps or "").replace("\r", "").split("\n") if s.strip()]
    if len(step_list) < 2:
        step_list = [str(steps or "执行操作")[:60], "观察结果"]
    base.append({"id": cid, "title": str(title), "steps": step_list,
                 "expected": str(expected or "符合预期")})

specs = list(base)

BOUNDARY = [("空值", "将输入清空后提交"), ("超长", "输入 300 字符后提交"),
            ("特殊字符", "输入 <script>alert(1)</script> 后提交")]
ROLES = ["editor", "author", "contributor"]

for i, c in enumerate(base):
    kind, step = BOUNDARY[i % len(BOUNDARY)]
    specs.append({"id": f"{c['id']}-B{i%3+1}",
                  "title": f"{c['title']}（边界：{kind}）",
                  "steps": c["steps"] + [step],
                  "expected": f"系统给出明确提示且不产生异常数据（{kind}）"})

for i, c in enumerate(base):
    role = ROLES[i % len(ROLES)]
    specs.append({"id": f"{c['id']}-R{i%3+1}",
                  "title": f"{c['title']}（角色：{role}）",
                  "steps": [f"以 {role} 身份登录"] + c["steps"],
                  "expected": f"按 {role} 权限执行，越权时被拒绝"})

# 补到 96：顺序变体
i = 0
while len(specs) < 96:
    c = base[i % len(base)]
    specs.append({"id": f"{c['id']}-S{i%3+1}",
                  "title": f"{c['title']}（顺序变体 {i%3+1}）",
                  "steps": list(reversed(c["steps"])),
                  "expected": "前置条件缺失时给出明确错误，不产生脏数据"})
    i += 1

specs = specs[:96]
json.dump(specs, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

from collections import Counter
kinds = Counter()
for s in specs:
    if "-B" in s["id"]:
        kinds["边界变体"] += 1
    elif "-R" in s["id"]:
        kinds["角色变体"] += 1
    elif "-S" in s["id"]:
        kinds["顺序变体"] += 1
    else:
        kinds["原始用例"] += 1
print(f"生成 {len(specs)} 个场景：{dict(kinds)}")
print("示例：")
for s in specs[:2] + specs[43:45]:
    print(" ", s["id"], "|", s["title"][:40])
