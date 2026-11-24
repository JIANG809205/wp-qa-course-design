# -*- coding: utf-8 -*-
"""提取示例报告的精确格式参数，供生成器复刻。"""

from docx import Document
from docx.shared import Pt

SRC = r"E:\软件质量保证与测试课程设计\（示例）课程设计报告-学号-姓名.docx"
doc = Document(SRC)

for name in ("Normal", "Heading 1", "Heading 2", "Heading 3", "图表标题"):
    try:
        st = doc.styles[name]
    except KeyError:
        print(f"{name}: 不存在")
        continue
    f, pf = st.font, st.paragraph_format
    print(f"=== {name} ===")
    print(f"  字体: name={f.name} size={f.size.pt if f.size else None} bold={f.bold}")
    print(f"  段落: 行距={pf.line_spacing} 行距规则={pf.line_spacing_rule} "
          f"段前={pf.space_before.pt if pf.space_before else None} "
          f"段后={pf.space_after.pt if pf.space_after else None} "
          f"首行缩进={pf.first_line_indent.cm if pf.first_line_indent else None} "
          f"对齐={pf.alignment}")
    try:
        rpr = st.element.rPr
        ea = rpr.rFonts.get(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia")
        print(f"  中文字体(eastAsia)={ea}")
    except Exception as e:  # noqa: BLE001
        print("  eastAsia 读取失败:", e)

# 章节号统计：看标题前是否带编号
print("\n=== 各级标题原文（前 20 个）===")
n = 0
for p in doc.paragraphs:
    if p.style.name in ("Heading 1", "Heading 2", "Heading 3") and p.text.strip():
        print(f"  [{p.style.name}] {p.text.strip()[:50]}")
        n += 1
        if n >= 20:
            break
