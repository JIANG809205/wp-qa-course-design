# -*- coding: utf-8 -*-
"""按示例模板排版生成报告 docx。

复刻示例格式：
- 页面 A4，上下 2.5cm、左右 3.2cm
- 正文 Times New Roman + 宋体 12pt（小四），1.2 倍行距，首行缩进 2 字符，两端对齐
- 一级标题 黑体 14pt，二/三级 黑体 12pt，段前段后按示例
- 图表标题：宋体 10.5pt 加粗居中
- 页脚居中页码
"""

from __future__ import annotations

import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = r"E:\软件质量保证与测试课程设计"
SRC = os.path.join(ROOT, "报告-按示例模板.md")
OUT = os.environ.get("OUT_DOCX") or os.path.join(ROOT, "课程设计报告-学号-姓名.docx")

FIG = {
    "perf-tps": "wp-perf/charts-final/perf-tps.png",
    "perf-p95": "wp-perf/charts-final/perf-p95.png",
    "perf-cpu": "wp-perf/charts-final/perf-cpu.png",
    "llm-fidelity": "wp-perf/charts-final/llm-fidelity.png",
    "llm-runnable": "wp-perf/charts-final/llm-runnable.png",
    "defects": "wp-perf/charts-final/defects.png",
    "cases-by-module": "wp-perf/charts-final/cases-by-module.png",
    "permission-matrix": "wp-perf/charts-final/permission-matrix.png",
    "debug-log": "defect-hunt/evidence/debug-log.png",
    "uploads": "defect-hunt/evidence/uploads-index.png",
    "site": "wp-env/screenshots/shot-main.png",
    "posts": "wp-env/screenshots/shot-posts.png",
    "admin": "wp-env/screenshots/shot-admin.png",
}

CN_QUOTE = re.compile(r'"([^"\n]{1,120})"')


def cn_quotes(s: str) -> str:
    return CN_QUOTE.sub(lambda m: "“" + m.group(1) + "”", s)



def _force_black(style_or_run_rpr):
    """清除主题色，避免 Word 用 themeColor 覆盖显式黑色。"""
    color = style_or_run_rpr.find(qn("w:color"))
    if color is None:
        return
    for attr in ("themeColor", "themeTint", "themeShade"):
        key = qn("w:" + attr)
        if key in color.attrib:
            del color.attrib[key]


def setup_styles(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    pf = st.paragraph_format
    pf.line_spacing = 1.2
    pf.first_line_indent = Cm(0.85)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    for name, size, before, after in (("Heading 1", 14, 6, 6),
                                      ("Heading 2", 12, 2.5, 2.5),
                                      ("Heading 3", 12, 2, 2)):
        s = doc.styles[name]
        s.font.name = "黑体"
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(s.element.rPr)
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        s.paragraph_format.space_before = Pt(before)
        s.paragraph_format.space_after = Pt(after)
        s.paragraph_format.first_line_indent = Cm(0)
        s.paragraph_format.line_spacing = 1.0

    cap = doc.styles.add_style("图表标题", 1)
    cap.font.size = Pt(10.5)
    cap.font.bold = True
    cap.font.name = "宋体"
    cap._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_before = Pt(3)
    cap.paragraph_format.space_after = Pt(3)


def add_page_number(section) -> None:
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run()
    for el, attrs, text in (("w:fldChar", {"w:fldCharType": "begin"}, None),
                            ("w:instrText", {"xml:space": "preserve"}, " PAGE "),
                            ("w:fldChar", {"w:fldCharType": "end"}, None)):
        e = OxmlElement(el)
        for k, v in attrs.items():
            e.set(qn(k) if ":" in k else k, v)
        if text is not None:
            e.text = text
        run._r.append(e)
    run.font.size = Pt(10.5)


def add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.85)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    text = cn_quotes(text.replace("`", ""))
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if not part:
            continue
        r = p.add_run(part[2:-2] if part.startswith("**") else part)
        r.bold = part.startswith("**")
        r.font.size = Pt(12)
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def add_heading(doc: Document, text: str, level: int, title: bool = False) -> None:
    if level == 1 and not title:
        doc.add_page_break()
    p = doc.add_paragraph(style=f"Heading {min(level, 3)}")
    p.paragraph_format.first_line_indent = Cm(0)
    if title:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(120)
        r = p.add_run(text)
        r.font.name = "黑体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(r._element.get_or_add_rPr())
    else:
        r = p.add_run(text)
        r.font.name = "黑体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        r.font.size = Pt({1: 14, 2: 12, 3: 12}[min(level, 3)])
        r.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(r._element.get_or_add_rPr())


def add_caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="图表标题")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(cn_quotes(text))
    r.font.size = Pt(10.5)
    r.bold = True
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def add_code(doc: Document, code_lines: list[str]) -> None:
    for ln in code_lines:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.85)
        r = p.add_run(ln if ln.strip() else " ")
        r.font.name = "Consolas"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r.font.size = Pt(9.5)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "F4F4F4")
        pPr.append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_figure(doc: Document, key: str, cap: str) -> None:
    rel = FIG.get(key)
    if not rel:
        print("未登记的图:", key)
        return
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        print("缺图文件:", rel)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.add_run().add_picture(path, width=Cm(14.0))
    add_caption(doc, cap)


def add_table(doc: Document, raw: list[str]) -> None:
    rows = []
    for ln in raw:
        cells = [c.strip().replace("`", "").replace("**", "")
                 for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append([cn_quotes(c) for c in cells])
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    tb = doc.add_table(rows=len(rows), cols=ncol)
    tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j in range(ncol):
            cell = tb.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(row[j] if j < len(row) else "")
            r.font.size = Pt(10)
            r.font.name = "Times New Roman"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            r.bold = (i == 0)
    tblPr = tb._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, w in (("top", 20), ("bottom", 20), ("left", 80), ("right", 80)):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:w"), str(w))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)
    for row in tb.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    tb.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def build() -> None:
    doc = Document()
    setup_styles(doc)
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)
        s.left_margin, s.right_margin = Cm(3.2), Cm(3.2)
        add_page_number(s)

    lines = open(SRC, encoding="utf-8").read().splitlines()
    i = 0
    first_h1 = True
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue

        m = re.match(r"^\[\[图:([A-Za-z0-9\-]+)\|(.+)\]\]$", s)
        if m:
            add_figure(doc, m.group(1), m.group(2))
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            add_code(doc, code)
            continue

        if s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and first_h1:
                add_heading(doc, text, 1, title=True)
                first_h1 = False
            else:
                add_heading(doc, text, level)
            i += 1
            continue

        if re.match(r"^(表|图)\s*\d+\.\d+", s):
            add_caption(doc, s)
            i += 1
            continue

        if s.startswith("---"):
            i += 1
            continue

        add_body(doc, s)
        i += 1

    doc.save(OUT)
    print("已生成:", OUT)
    print("段落:", len(doc.paragraphs), "表格:", len(doc.tables), "图片:", len(doc.inline_shapes))


if __name__ == "__main__":
    build()
