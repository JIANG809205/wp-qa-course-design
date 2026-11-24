# -*- coding: utf-8 -*-
"""表格更紧凑：字号 10pt、单元格边距收紧、标题与表格同页。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"
t = io.open(P, encoding="utf-8").read()

# 1) 图表标题与后续表格保持同页
t = t.replace("""    p = doc.add_paragraph(style="图表标题")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(cn_quotes(text))""",
              """    p = doc.add_paragraph(style="图表标题")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(cn_quotes(text))""")

# 2) 表格字号 10pt + 收紧单元格边距
t = t.replace("""            r.font.size = Pt(10.5)
            r.font.name = "Times New Roman"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            r.bold = (i == 0)""",
              """            r.font.size = Pt(10)
            r.font.name = "Times New Roman"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            r.bold = (i == 0)""")

t = t.replace("""    for row in tb.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))""",
              """    tblPr = tb._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, w in (("top", 20), ("bottom", 20), ("left", 80), ("right", 80)):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:w"), str(w))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)
    for row in tb.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("表格紧凑化已应用")
