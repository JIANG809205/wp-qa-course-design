# -*- coding: utf-8 -*-
"""把 Markdown 报告章节合成为课程设计报告 docx（宋体小四、图表居中、标题层级）。"""

from __future__ import annotations

import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = r"E:\软件质量保证与测试课程设计"
OUT = os.path.join(ROOT, "课程设计报告-学号-姓名.docx")

SOURCES = [
    (os.path.join(ROOT, "报告正文-第1-3章.md"), None),
    (os.path.join(ROOT, "报告正文-第4-5章.md"), None),
    (os.path.join(ROOT, "06-报告章节-大模型使用过程及经验.md"), None),
    (os.path.join(ROOT, "报告正文-第7-9章.md"), None),
]

FIGS = {
    "perf-tps": os.path.join(ROOT, "wp-perf", "charts-final", "perf-tps.png"),
    "perf-p95": os.path.join(ROOT, "wp-perf", "charts-final", "perf-p95.png"),
    "perf-cpu": os.path.join(ROOT, "wp-perf", "charts-final", "perf-cpu.png"),
    "llm-fidelity": os.path.join(ROOT, "wp-perf", "charts-final", "llm-fidelity.png"),
    "llm-runnable": os.path.join(ROOT, "wp-perf", "charts-final", "llm-runnable.png"),
    "defects": os.path.join(ROOT, "wp-perf", "charts-final", "defects.png"),
    "cases-by-module": os.path.join(ROOT, "wp-perf", "charts-final", "cases-by-module.png"),
    "permission-matrix": os.path.join(ROOT, "wp-perf", "charts-final", "permission-matrix.png"),
    "debug-log": os.path.join(ROOT, "defect-hunt", "evidence", "debug-log.png"),
    "uploads": os.path.join(ROOT, "defect-hunt", "evidence", "uploads-index.png"),
    "site": os.path.join(ROOT, "wp-env", "screenshots", "shot-main.png"),
    "mobile-admin": os.path.join(ROOT, "wp-compat", "screenshots", "mobile-375-admin.png"),
}

# 章节中插入图的位置：heading 文本片段 -> (图 key, 图题)
INSERT_AFTER = [
    ("5.4 权限矩阵", ("permission-matrix", "图 5-1　权限矩阵实测：36 格全部符合预期")),
    ("5.5 兼容性测试", ("mobile-admin", "图 5-2　375px 视口下后台自动切换移动布局")),
    ("7.2 P1 级缺陷详述", ("debug-log", "图 7-1　DEF-002 证据：debug.log 可匿名下载并泄露绝对路径")),
    ("8.2 性能结果", ("perf-tps", "图 8-1　吞吐量随并发变化（60 秒稳态 × 3 次）")),
    ("8.3 性能结论", ("perf-p95", "图 8-2　P95 响应时间：列表页 100 并发突破 2 秒")),
    ("8.4 优化实验", ("perf-cpu", "图 8-3　压测期间容器 CPU 稳定占用 6–6.8 核")),
    ("6.4.3", ("llm-fidelity", "图 6-1　定位器保真度三次修正后收敛到 21%–29%")),
    ("6.4.4", ("llm-runnable", "图 6-2　结构可运行 vs 严格可运行：差距即定位器幻觉")),
    ("5.2 分模块结果", ("cases-by-module", "图 5-3　各模块用例执行结果")),
    ("7.6 缺陷分布", ("defects", "图 7-2　缺陷等级分布")),
]


def set_base_style(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "宋体"
    st.font.size = Pt(12)  # 小四
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def add_heading(doc: Document, text: str, level: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    run.font.size = Pt({1: 16, 2: 14, 3: 12}.get(level, 12))
    run.bold = True
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)  # 2 字符
    p.paragraph_format.space_after = Pt(3)
    # 处理 **加粗**
    text = text.replace("`", "")
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        else:
            r = p.add_run(part)
        r.font.name = "宋体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r.font.size = Pt(12)


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(2)
    text = text.replace("`", "")
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        r = p.add_run(part[2:-2] if part.startswith("**") else part)
        r.bold = part.startswith("**")
        r.font.name = "宋体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r.font.size = Pt(12)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j in range(ncol):
            cell = table.cell(i, j)
            cell.text = (row[j] if j < len(row) else "").replace("`", "").replace("**", "")
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                for r in p.runs:
                    r.font.name = "宋体"
                    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
                    r.font.size = Pt(10.5)
                    if i == 0:
                        r.bold = True
    from docx.oxml import OxmlElement

    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
    hdr = table.rows[0]._tr.get_or_add_trPr()
    hdr.append(OxmlElement("w:tblHeader"))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_figure(doc: Document, key: str, caption: str) -> None:
    path = FIGS.get(key)
    if not path or not os.path.exists(path):
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.add_run().add_picture(path, width=Cm(14.5))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_after = Pt(8)
    r = cap.add_run(caption)
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(10.5)
    r.bold = True


def parse_table(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def convert(doc: Document, md_path: str) -> None:
    if not os.path.exists(md_path):
        print("跳过（不存在）:", md_path)
        return
    lines = open(md_path, encoding="utf-8").read().splitlines()
    i = 0
    pending = list(INSERT_AFTER)
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        # 代码块
        if line.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                add_para(doc, lines[i])
                i += 1
            i += 1
            continue
        # 表格
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, parse_table(block))
            continue
        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and text.startswith("第"):
                doc.add_page_break()
            add_heading(doc, text, min(level, 3))
            for frag, (key, cap) in list(pending):
                if frag in text:
                    add_figure(doc, key, cap)
                    pending.remove((frag, (key, cap)))
            i += 1
            continue
        if line.startswith("---"):
            i += 1
            continue
        if line.startswith(">"):
            add_para(doc, line.lstrip("> ").strip())
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            add_bullet(doc, re.sub(r"^\s*[-*]\s+", "", line))
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            add_bullet(doc, re.sub(r"^\s*\d+\.\s+", "", line))
            i += 1
            continue
        add_para(doc, line)
        i += 1


def main() -> None:
    doc = Document()
    set_base_style(doc)
    for s in doc.sections:
        s.top_margin = Cm(2.54)
        s.bottom_margin = Cm(2.54)
        s.left_margin = Cm(3.0)
        s.right_margin = Cm(2.6)

    # 封面
    for _ in range(4):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("《软件质量保证与测试》课程设计报告")
    r.font.name = "黑体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r.font.size = Pt(22)
    r.bold = True

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = sub.add_run("基于 DeepSeek 的开源 CMS 系统 Web 测试与质量评估\n——以 WordPress 为例")
    r2.font.name = "黑体"
    r2._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    r2.font.size = Pt(16)

    for _ in range(6):
        doc.add_paragraph()
    info = [("专　　业", "软件工程"), ("班　　级", "软件 2201"),
            ("学　　号", ""), ("姓　　名", ""), ("指导教师", ""),
            ("完成日期", "2026 年 11 月")]
    for k, v in info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rr = p.add_run(f"{k}：{v if v else '　' * 10}")
        rr.font.name = "宋体"
        rr._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        rr.font.size = Pt(14)

    doc.add_page_break()

    # 正文
    for path, _ in SOURCES:
        convert(doc, path)

    doc.save(OUT)
    print("已生成:", OUT)
    print("段落数:", len(doc.paragraphs), "表格数:", len(doc.tables))


if __name__ == "__main__":
    main()
