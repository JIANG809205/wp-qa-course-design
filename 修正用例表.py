# -*- coding: utf-8 -*-
"""修正 05-测试用例 工作簿：
1) 权限实测页缺 auditor（30 → 36 格，取自 defect-hunt/matrix-reps/rep1.json）
2) 权限矩阵页数据错行（第 4 行角色写成"验证方法"），按实测 json 的预期值整页重建
3) 执行汇总的"权限矩阵 30 格""失败用例关联缺陷"两处笔误
4) 兼容性 3 行归因列误填日期（移到执行日期列）
"""

import json
import os

import openpyxl

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(ROOT, "05-测试用例-核心40条.xlsx")

rep = json.load(open(os.path.join(ROOT, "defect-hunt", "matrix-reps", "rep1.json"), encoding="utf-8"))
EXP = {"Y": "允许", "N": "拒绝", "C": "有条件"}

wb = openpyxl.load_workbook(XLSX)

# ---------- 1. 权限实测：整页按 json 重建 36 行 ----------
idx = wb.sheetnames.index("权限实测")
del wb["权限实测"]
ws = wb.create_sheet("权限实测", idx)
hdr = ["角色", "操作", "预期", "页面状态", "页面元素", "接口结果", "判定", "接口返回摘要"]
for j, v in enumerate(hdr, start=1):
    ws.cell(1, j, v)
role_cn = {"admin": "admin", "editor": "editor", "author": "author",
           "contributor": "contributor", "subscriber": "subscriber", "auditor": "auditor"}
for i, r in enumerate(rep, start=2):
    exp = EXP.get(str(r["expect"]).strip(), str(r["expect"]))
    ok = (exp == "允许" and r["api"] == "allow") or \
         (exp == "拒绝" and r["api"] == "deny") or \
         (exp == "有条件" and r["api"] in ("allow", "allow_pending"))
    ws.cell(i, 1, role_cn.get(r["role"], r["role"]))
    ws.cell(i, 2, r.get("name"))
    ws.cell(i, 3, exp)
    ws.cell(i, 4, r.get("ui_status"))
    ws.cell(i, 5, "存在" if r.get("ui_marker") else ("缺失" if r.get("ui_denied") else "—"))
    ws.cell(i, 6, r.get("api"))
    ws.cell(i, 7, "符合" if ok else "不符")
    ws.cell(i, 8, str(r.get("api_msg"))[:180])
print(f"权限实测页已重建：{len(rep)} 格")

# ---------- 2. 权限矩阵页：整页重建 ----------
roles_order = ["admin", "editor", "author", "contributor", "subscriber", "auditor"]
role_cn2 = {"admin": "管理员", "editor": "编辑", "author": "作者",
            "contributor": "投稿者", "subscriber": "订阅者", "auditor": "auditor（自定义）"}
note = {"admin": "站点所有者，全部权限", "editor": "内容负责人，无用户与设置权限",
        "author": "仅能发布/管理自己的文章", "contributor": "只能提交待审稿件",
        "subscriber": "仅管理个人资料", "auditor": "仅 read / edit_posts / moderate_comments"}
ops_order = ["OP1", "OP2", "OP3", "OP4", "OP5", "OP6"]
ops_cn = {"OP1": "OP1 发布文章", "OP2": "OP2 编辑他人文章", "OP3": "OP3 审核评论",
          "OP4": "OP4 上传媒体", "OP5": "OP5 新建用户", "OP6": "OP6 修改设置"}
grid = {(r["role"], r["op"]): EXP.get(str(r["expect"]).strip(), "") for r in rep}

idx = wb.sheetnames.index("权限矩阵")
del wb["权限矩阵"]
ws2 = wb.create_sheet("权限矩阵", idx)
ws2["A1"] = "6 角色 × 6 操作 权限矩阵（预期，依据 WordPress 能力模型与自定义角色设计）"
ws2.merge_cells("A1:H1")
for j, v in enumerate(["角色"] + [ops_cn[o] for o in ops_order] + ["说明"], start=1):
    ws2.cell(3, j, v)
for i, role in enumerate(roles_order, start=4):
    ws2.cell(i, 1, role_cn2[role])
    for j, op in enumerate(ops_order, start=2):
        ws2.cell(i, j, grid.get((role, op), ""))
    ws2.cell(i, 8, note[role])
ws2.cell(11, 1, "判定规则：通道 A（UI 元素）与通道 B（带 nonce 的接口请求）双通道验证，"
                "两层都拒绝才判定权限控制有效；UI 隐藏但请求成功记为权限绕过缺陷。")
ws2.merge_cells("A11:H11")
print("权限矩阵页已重建")

# ---------- 3. 执行汇总 ----------
ws3 = wb["执行汇总"]
for row in ws3.iter_rows(min_row=1):
    k, v = row[0].value, row[1].value
    if k and "权限矩阵" in str(k) and v and "30 格" in str(v):
        row[1].value = str(v).replace("30 格", "36 格")
        print("执行汇总修正:", k, "→", row[1].value)
    if k and "失败用例关联缺陷" in str(k):
        row[1].value = "DEF-001、DEF-006、DEF-008、DEF-009"
        print("执行汇总修正:", k, "→", row[1].value)

# ---------- 4. 归因列错位 ----------
ws4 = wb["测试用例"]
hdr4 = [c.value for c in ws4[1]]
i_attr = hdr4.index("归因") + 1
i_date = hdr4.index("执行日期") + 1
fixed = 0
for row in ws4.iter_rows(min_row=2):
    if not row[0].value:
        continue
    attr = row[i_attr - 1].value
    if attr and str(attr).startswith("2026-"):
        row[i_date - 1].value = attr
        row[i_attr - 1].value = None
        fixed += 1
print("归因列错位修复:", fixed, "行")

wb.save(XLSX)
print("已保存:", XLSX)
