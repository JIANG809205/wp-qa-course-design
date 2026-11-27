# -*- coding: utf-8 -*-
"""补回表格防拆行，并压缩追溯矩阵用例范围写法。"""

import io
import os
import re

ROOT = r"E:\软件质量保证与测试课程设计"
GEN = os.path.join(ROOT, "生成报告docx-模板.py")
MD = os.path.join(ROOT, "报告-按示例模板.md")

# ---------- 1) add_table 里补 cantSplit ----------
t = io.open(GEN, encoding="utf-8").read()
anchor = '    tb.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))'
add = '''    for row in tb.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    tb.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))'''
if "w:cantSplit" not in t:
    t = t.replace(anchor, add, 1)
    io.open(GEN, "w", encoding="utf-8", newline="\n").write(t)
    print("已补回 cantSplit")
else:
    print("cantSplit 已存在")

# ---------- 2) 追溯矩阵压缩写法 ----------
m = io.open(MD, encoding="utf-8").read()


def shrink(match):
    pre, start, end = match.group(1), match.group(2), match.group(3)
    return f"{pre}{start}~{end}"


pattern = re.compile(r"(TC-[A-Z]+-)(\d{3})\s*~\s*(TC-[A-Z]+-)(\d{3})")
m2 = pattern.sub(lambda x: f"{x.group(1)}{x.group(2)}~{x.group(4)}", m)
io.open(MD, "w", encoding="utf-8", newline="\n").write(m2)
print("压缩追溯矩阵写法:", len(pattern.findall(m)), "处")
