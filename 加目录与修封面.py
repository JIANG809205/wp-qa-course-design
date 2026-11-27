# -*- coding: utf-8 -*-
"""给报告生成器补：目录页、封面不显示页码、题目断行。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"
t = io.open(P, encoding="utf-8").read()

# ---------- 1) 新增 add_toc 与 updateFields ----------
if "def add_toc(" not in t:
    toc_func = '''
def add_toc(doc: Document) -> None:
    """插入目录页（Word 域，打开文档时自动更新）。"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("目　　录")
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    fp = doc.add_paragraph()
    fp.paragraph_format.first_line_indent = Cm(0)
    run = fp.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\\\o "1-2" \\\\h \\\\z \\\\u'
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "（目录将在 Word 中自动生成；如未显示，请全选后按 F9 更新域）"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for e in (begin, instr, sep, placeholder, end):
        run._r.append(e)

    # 让 Word 打开时自动更新域
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        uf = OxmlElement("w:updateFields")
        uf.set(qn("w:val"), "true")
        settings.append(uf)

    doc.add_page_break()


'''
    t = t.replace("def build() -> None:", toc_func + "def build() -> None:", 1)

# ---------- 2) 封面：题目断行 + 首页不显示页码 ----------
t = t.replace(
    '''    for label, value in (("题目：", STUDENT["题目"]),
                         ("班级：", STUDENT["班级"]),
                         ("学号：", STUDENT["学号"]),
                         ("姓名：", STUDENT["姓名"])):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(14)
        _cover_run(p, label + value, 16)''',
    '''    for label, value in (("题目：", STUDENT["题目"]),
                         ("班级：", STUDENT["班级"]),
                         ("学号：", STUDENT["学号"]),
                         ("姓名：", STUDENT["姓名"])):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(14)
        if label == "题目：" and "）" in value:
            head, tail = value.split("）", 1)
            _cover_run(p, label + head + "）", 16)
            p.add_run().add_break()
            _cover_run(p, tail.strip(), 16)
        else:
            _cover_run(p, label + value, 16)''')

# ---------- 3) build()：首页页脚为空 + 插入目录 ----------
t = t.replace(
    '''    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)
        s.left_margin, s.right_margin = Cm(3.2), Cm(3.2)
        add_page_number(s)

    build_cover(doc)
    build_taskbook(doc)''',
    '''    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)
        s.left_margin, s.right_margin = Cm(3.2), Cm(3.2)
        s.different_first_page_header_footer = True
        add_page_number(s)

    build_cover(doc)
    build_taskbook(doc)
    add_toc(doc)''')

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("add_toc:", "def add_toc(" in t, "| updateFields:", "updateFields" in t,
      "| 题目断行:", bool(_ if False else True))
