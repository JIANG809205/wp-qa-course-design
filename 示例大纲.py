# -*- coding: utf-8 -*-
"""输出示例报告的完整标题大纲与结尾部分。"""

from docx import Document

SRC = r"E:\软件质量保证与测试课程设计\（示例）课程设计报告-学号-姓名.docx"
doc = Document(SRC)

print("=" * 80)
print("完整标题大纲")
print("=" * 80)
for p in doc.paragraphs:
    t = p.text.strip()
    if not t:
        continue
    st = p.style.name
    if st in ("Heading 1", "Heading 2", "Heading 3"):
        indent = {"Heading 1": "", "Heading 2": "  ", "Heading 3": "    "}[st]
        size = max((r.font.size.pt for r in p.runs if r.font.size), default=0)
        print(f"{indent}[{st}] {t[:60]}  (字号={size})")

print()
print("=" * 80)
print(f"总段落数 {len(doc.paragraphs)}；最后 45 段")
print("=" * 80)
for i, p in enumerate(doc.paragraphs[-45:], start=len(doc.paragraphs) - 45):
    t = p.text.strip()
    print(f"[{i}] {p.style.name:<10} | {t[:60]}")
