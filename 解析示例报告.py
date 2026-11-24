# -*- coding: utf-8 -*-
"""解析示例报告的完整格式：封面、章节结构、字体字号、行距、缩进、表格样式。"""

from __future__ import annotations

import re

from docx import Document
from docx.shared import Pt

SRC = r"E:\软件质量保证与测试课程设计\（示例）课程设计报告-学号-姓名.docx"
doc = Document(SRC)

print("=" * 90)
print("一、页面设置")
for i, s in enumerate(doc.sections):
    print(f"  节 {i}: 页宽 {s.page_width.cm:.1f}cm 页高 {s.page_height.cm:.1f}cm "
          f"上 {s.top_margin.cm:.1f} 下 {s.bottom_margin.cm:.1f} "
          f"左 {s.left_margin.cm:.1f} 右 {s.right_margin.cm:.1f}")

print("=" * 90)
print("二、样式定义（被文档实际使用的）")
used = {}
for p in doc.paragraphs:
    used.setdefault(p.style.name, 0)
    used[p.style.name] += 1
for name, cnt in sorted(used.items(), key=lambda x: -x[1]):
    st = doc.styles[name] if name in [s.name for s in doc.styles] else None
    if st is None:
        print(f"  {name}: {cnt} 段")
        continue
    f = st.font
    pf = st.paragraph_format
    print(f"  {name}: {cnt} 段 | 字体={f.name} 字号={f.size.pt if f.size else None} 粗体={f.bold} "
          f"| 行距={pf.line_spacing} 首行缩进={pf.first_line_indent.cm if pf.first_line_indent else None} "
          f"对齐={pf.alignment}")

print("=" * 90)
print("三、全文段落明细（前 120 段）")
for i, p in enumerate(doc.paragraphs[:120]):
    t = p.text.strip()
    pf = p.paragraph_format
    sizes = {r.font.size.pt for r in p.runs if r.font.size}
    fonts = {r.font.name for r in p.runs if r.font.name}
    bold = any(r.bold for r in p.runs)
    print(f"[{i:>3}] {p.style.name:<12} "
          f"字号={sorted(sizes) if sizes else '-'} 字体={sorted(f for f in fonts if f)} "
          f"粗={int(bold)} 缩进={pf.first_line_indent.cm if pf.first_line_indent else 0} "
          f"行距={pf.line_spacing} 对齐={pf.alignment} | {t[:50]}")

print("=" * 90)
print("四、文档结构（标题类段落）")
for p in doc.paragraphs:
    t = p.text.strip()
    if not t:
        continue
    style = p.style.name
    is_bold = any(r.bold for r in p.runs)
    size = max((r.font.size.pt for r in p.runs if r.font.size), default=0)
    if style.startswith("Heading") or (is_bold and size >= 12) or re.match(r"^(第[一二三四五六七八九十]+[章部分]|[一二三四五六七八九十]+、|\d+(\.\d+)*\s)", t):
        print(f"  [{style}] 字号={size} | {t[:70]}")

print("=" * 90)
print(f"五、表格 {len(doc.tables)} 个")
for i, tb in enumerate(doc.tables[:6]):
    print(f"  表 {i}: {len(tb.rows)} 行 × {len(tb.columns)} 列, 样式={tb.style.name if tb.style else None}")
    for r in tb.rows[:2]:
        print("     |", " | ".join(c.text.strip()[:14] for c in r.cells))

print("=" * 90)
print("六、页眉页脚")
for i, s in enumerate(doc.sections):
    hdr = [p.text for p in s.header.paragraphs if p.text.strip()]
    ftr = [p.text for p in s.footer.paragraphs if p.text.strip()]
    print(f"  节 {i}: 页眉={hdr} 页脚={ftr}")
