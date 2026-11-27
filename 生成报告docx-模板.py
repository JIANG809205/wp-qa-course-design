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

STUDENT = {
    "题目": "基于大模型的开源CMS系统（WordPress）Web测试",
    "班级": "软件2401",
    "学号": "241303109",
    "姓名": "蒋晓涵",
}

COURSE_GOAL = (
    "课程目标：\n"
    "（1）掌握软件质量保证与测试的基础知识和理论、基本方法和技术，理解影响软件质量保证与测试的各种因素。"
    "（2）掌握软件测试设计方法，能够针对特定测试需求，设计测试用例，开发测试脚本，执行测试并分析测试结果。"
    "（3）能认识到软件测试有多种可选方案，并能通过查阅资料，分析研究，寻找可替代的软件测试问题解决方案。"
    "（4）掌握软件工程质量保证方法，理解软件测试在软件开发过程中的重要性，并能根据项目需求进行合理的测试计划和测试用例设计。"
    "（5）熟悉常用的软件测试工具和技术，掌握自动化测试和持续集成等先进的软件测试方法。"
    "（6）通过实践项目，培养学生的团队协作和沟通能力，提高学生的实践能力和综合素质。"
)

TASKBOOK_BODY = (
    "课题名称、主要目标和具体要求：\n"
    "1.课题名称：基于大模型的开源CMS系统（WordPress）Web测试\n"
    "2.主要目标：\n"
    "掌握Web测试概念、流程和方法。深入理解大模型在Web测试中的应用方式与局限。"
    "熟悉Selenium、pytest、JMeter等自动化与性能测试工具。能够针对实际Web应用设计并执行有效的测试方案。"
    "通过测试数据分析，识别问题并为质量改进提供建议。培养独立分析、交叉复核与工程规范意识。\n"
    "3.具体要求：\n"
    "设计并执行针对开源CMS系统WordPress的完整Web测试，覆盖功能、接口、权限、性能、安全与兼容性；"
    "在测试全流程中引入大模型完成需求到用例、用例到脚本、失败日志归因三项任务，"
    "并以结构合规率、定位器保真度、可运行率、归因准确率等指标量化大模型产出的真实可用性；"
    "提交测试计划、测试用例、缺陷清单与课程设计报告。\n"
    "进程安排：\n"
    "2026年11月—12月，共4周：第1周开题论证与环境搭建；第2周功能与接口测试；"
    "第3周性能与安全测试；第4周大模型评测与报告撰写。"
)

TEAM_ROWS = [
    ("蒋晓涵（本人）", "选题论证、环境搭建、用例设计与执行、大模型评测、报告撰写"),
    ("同学A", "测试用例与权限矩阵交叉评审"),
    ("同学B", "缺陷定级与报告初稿复核"),
]

GRADE_ROWS = [
    ("1", "测试需求分析", "20%", ""),
    ("2", "测试计划&测试用例设计", "30%", ""),
    ("3", "自动测试工具", "30%", ""),
    ("4", "测试报告&答辩", "20%", ""),
    ("", "总成绩", "100%", ""),
]

FIG = {
    "flow-test": "diagrams/flow-test.png",
    "flow-state": "diagrams/flow-state.png",
    "defect-flow": "diagrams/defect-flow.png",
    "fix-compare": "diagrams/fix-compare.png",
    "env-topology": "diagrams/env-topology.png",
    "llm-workflow": "diagrams/llm-workflow.png",
    "ci-pipeline": "diagrams/ci-pipeline.png",
    "perf-chain": "diagrams/perf-chain.png",
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
    "perf-box": "wp-perf/charts-final/perf-box.png",
    "defects-by-module": "wp-perf/charts-final/defects-by-module.png",
    "ev-mvn": "evidence/mvn-test.png",
    "ev-pytest": "evidence/pytest.png",
    "ev-matrix": "evidence/matrix.png",
    "ev-probe": "evidence/probe-compare.png",
    "compat-mobile": "wp-compat/screenshots/mobile-pair.png",
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
    # 章节连续排版，不做强制分页，避免短章节或文末孤行留下大片空白
    p = doc.add_paragraph(style=f"Heading {min(level, 3)}")
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    if title:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(72)
        p.paragraph_format.space_after = Pt(18)
        # 长标题在 " Web " 前断行，避免末尾几个字单独折行
        if len(text) > 24 and " Web " in text:
            left, right = text.split(" Web ", 1)
            r = p.add_run(left)
            r.font.name = "黑体"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
            r.font.size = Pt(18)
            r.font.color.rgb = RGBColor(0, 0, 0)
            r.add_break()
            r2 = p.add_run("Web " + right)
            r2.font.name = "黑体"
            r2._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
            r2.font.size = Pt(18)
            r2.font.color.rgb = RGBColor(0, 0, 0)
            return
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


def add_caption(doc: Document, text: str, keep_next: bool = False) -> None:
    p = doc.add_paragraph(style="图表标题")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = keep_next
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
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    # 横版图表按宽度 11.3cm；竖版截图按高度 8.5cm；拼版截图单独指定宽度
    override = {"compat-mobile": 10.4,
            "env-topology": 15.2, "flow-test": 15.2, "flow-state": 15.2,
            "defect-flow": 15.2, "llm-workflow": 15.2, "ci-pipeline": 15.2,
            "perf-chain": 15.2, "fix-compare": 13.6}
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
        if key in override:
            run.add_picture(path, width=Cm(override[key]))
        elif h / w > 1.2:
            run.add_picture(path, height=Cm(8.5))
        else:
            run.add_picture(path, width=Cm(11.3))
    except Exception:
        run.add_picture(path, width=Cm(11.3))
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
    # 表头跨页重复；不强制整表不断页，避免整表跳页留下大片空白
    for row in tb.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    tb.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _cover_run(p, text, size, font="仿宋", bold=True):
    r = p.add_run(text)
    r.font.name = font
    r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    r.font.size = Pt(size)
    r.bold = bold
    r.font.color.rgb = RGBColor(0, 0, 0)
    return r


def _cell_text(cell, text, size=10.5, bold=False, align=None, name="宋体"):
    cell.text = ""
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        if align is not None:
            p.alignment = align
        r = p.add_run(ln)
        r.font.size = Pt(size)
        r.bold = bold
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def build_cover(doc: Document) -> None:
    # 标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(60)
    p.paragraph_format.space_after = Pt(36)
    _cover_run(p, "软件质量保证与测试课程设计", 26)

    # 题目 / 班级 / 学号 / 姓名
    for label, value in (("题目：", STUDENT["题目"]),
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
            _cover_run(p, label + value, 16)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 团队成员及任务分配
    tb = doc.add_table(rows=len(TEAM_ROWS) + 1, cols=2)
    tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    hc = tb.cell(0, 0).merge(tb.cell(0, 1))
    _cell_text(hc, "团队成员及任务分配", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, (name, duty) in enumerate(TEAM_ROWS, start=1):
        _cell_text(tb.cell(i, 0), name, align=WD_ALIGN_PARAGRAPH.CENTER)
        _cell_text(tb.cell(i, 1), duty)
    for row in tb.rows:
        row.cells[0].width = Cm(4.2)
        row.cells[1].width = Cm(10.6)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 评分表
    tb2 = doc.add_table(rows=len(GRADE_ROWS) + 1, cols=4)
    tb2.style = "Table Grid"
    tb2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(("序号", "项目名称", "考核比重", "得分")):
        _cell_text(tb2.cell(0, j), h, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, row in enumerate(GRADE_ROWS, start=1):
        for j, v in enumerate(row):
            _cell_text(tb2.cell(i, j), v, align=WD_ALIGN_PARAGRAPH.CENTER)
    tb2.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 日期
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    _cover_run(p, "2026年 12月", 16)
    doc.add_page_break()


def build_taskbook(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    _cover_run(p, "《软件质量保证与测试课程设计》任务书", 16, font="黑体")

    tb = doc.add_table(rows=5, cols=6)
    tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER

    head = ("课程编号", "21130418", "学分", "1", "周数", "1周")
    for j, v in enumerate(head):
        _cell_text(tb.cell(0, j), v, align=WD_ALIGN_PARAGRAPH.CENTER,
                   bold=(j % 2 == 0))
    for j, v in enumerate(("学号", STUDENT["学号"], "专业", "软件工程", "", "")):
        _cell_text(tb.cell(1, j), v, align=WD_ALIGN_PARAGRAPH.CENTER,
                   bold=(j % 2 == 0))
    for j, v in enumerate(("姓名", STUDENT["姓名"], "班级", STUDENT["班级"], "", "")):
        _cell_text(tb.cell(2, j), v, align=WD_ALIGN_PARAGRAPH.CENTER,
                   bold=(j % 2 == 0))

    goal_cell = tb.cell(3, 0).merge(tb.cell(3, 5))
    _cell_text(goal_cell, COURSE_GOAL)
    body_cell = tb.cell(4, 0).merge(tb.cell(4, 5))
    _cell_text(body_cell, TASKBOOK_BODY)

    doc.add_page_break()



def add_toc(doc: Document) -> None:
    """插入静态目录页：标题与页码来自 toc.json，未生成时用占位符。"""
    import json as _json
    import os as _os

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("目　　录")
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    toc_path = _os.path.join(ROOT, "toc.json")
    entries = []
    if _os.path.exists(toc_path):
        data = _json.load(open(toc_path, encoding="utf-8"))
        entries = data.get("entries", [])

    if not entries:
        # 无页码数据时，退化为仅列标题
        lines = open(SRC, encoding="utf-8").read().splitlines()
        for ln in lines:
            m = re.match(r"^(#{1,2})\s+(.*)$", ln.strip())
            if m:
                entries.append({"level": len(m.group(1)), "text": m.group(2).strip(), "page": "—"})

    from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    for e in entries:
        level = e.get("level", 1)
        text = e.get("text", "")
        page = str(e.get("page", "—"))
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0 if level == 1 else 0.85)
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(14.8), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = p.add_run(text + "\t" + page)
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r.font.size = Pt(12)
        r.bold = (level == 1)
        r.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()


def build() -> None:
    doc = Document()
    setup_styles(doc)
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)
        s.left_margin, s.right_margin = Cm(3.2), Cm(3.2)
        s.different_first_page_header_footer = True
        add_page_number(s)

    build_cover(doc)
    build_taskbook(doc)
    add_toc(doc)

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
            add_caption(doc, s, keep_next=s.startswith("表"))
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
