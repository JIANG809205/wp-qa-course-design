# -*- coding: utf-8 -*-
"""最终结构核对：标题层级、页数、图表数量、格式抽样。"""

import re

from docx import Document

P = r"E:\软件质量保证与测试课程设计\课程设计报告-学号-姓名.docx"
d = Document(P)

print("=== 标题结构 ===")
for p in d.paragraphs:
    t = p.text.strip()
    if p.style.name in ("Heading 1", "Heading 2", "Heading 3") and t:
        lvl = int(p.style.name[-1])
        indent = "  " * (lvl - 1)
        size = max((r.font.size.pt for r in p.runs if r.font.size), default=0)
        color = None
        for r in p.runs:
            if r.font.color and r.font.color.rgb:
                color = str(r.font.color.rgb)
                break
        print(f"{indent}{'#'*lvl} {t[:46]}  ({size}pt, 颜色={color})")

print()
print("=== 统计 ===")
print("段落:", len(d.paragraphs), "表格:", len(d.tables), "图片:", len(d.inline_shapes))
fig_caps = [p.text for p in d.paragraphs if re.match(r"^图\s*\d+\.\d+", p.text.strip())]
tab_caps = [p.text for p in d.paragraphs if re.match(r"^表\s*\d+\.\d+", p.text.strip())]
print("图标题:", len(fig_caps), "表标题:", len(tab_caps))

st = d.styles["Normal"]
print("正文样式:", st.font.name, st.font.size.pt, "行距", st.paragraph_format.line_spacing,
      "缩进", st.paragraph_format.first_line_indent.cm)
h1 = d.styles["Heading 1"]
print("一级标题:", h1.font.name, h1.font.size.pt)
sec = d.sections[0]
print("页面: %.1f x %.1f cm, 边距 上%.1f 下%.1f 左%.1f 右%.1f" % (
    sec.page_width.cm, sec.page_height.cm, sec.top_margin.cm, sec.bottom_margin.cm,
    sec.left_margin.cm, sec.right_margin.cm))
