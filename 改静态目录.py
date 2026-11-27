# -*- coding: utf-8 -*-
"""把目录域改为静态目录：读取 toc.json 的标题→页码，生成带点线对齐的目录。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"
t = io.open(P, encoding="utf-8").read()

start = t.find("def add_toc(")
end = t.find("def build() -> None:")
if start < 0 or end < 0:
    raise SystemExit("未找到 add_toc 或 build")

new_toc = '''def add_toc(doc: Document) -> None:
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
            m = re.match(r"^(#{1,2})\\s+(.*)$", ln.strip())
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
        r = p.add_run(text + "\\t" + page)
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r.font.size = Pt(12)
        r.bold = (level == 1)
        r.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()


'''

t = t[:start] + new_toc + t[end:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("目录函数已替换为静态目录；长度:", len(t))
