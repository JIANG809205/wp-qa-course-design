# -*- coding: utf-8 -*-
"""修正：表标题位置、标题主题色导致的蓝色。"""

import io
import re

MD = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
GEN = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"

# ---------- 1) 把夹在表头与分隔行之间的标题移到表头上方 ----------
lines = io.open(MD, encoding="utf-8").read().splitlines()
moved = 0
i = 0
while i < len(lines):
    s = lines[i].strip()
    if re.match(r"^表\s*\d+\.\d+", s) and i + 2 < len(lines):
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        nxt2 = lines[i + 2].strip() if i + 2 < len(lines) else ""
        if nxt.startswith("|") and re.match(r"^\|[\s:\-|]+\|$", nxt2):
            header = lines[i - 1].strip() if i > 0 else ""
            if header.startswith("|"):
                lines[i - 1] = s
                lines[i] = header
                moved += 1
    i += 1
io.open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("移动标题:", moved, "处")

# ---------- 2) 标题样式清除 themeColor ----------
t = io.open(GEN, encoding="utf-8").read()
add = '''
def _force_black(style_or_run_rpr):
    """清除主题色，避免 Word 用 themeColor 覆盖显式黑色。"""
    color = style_or_run_rpr.find(qn("w:color"))
    if color is None:
        return
    for attr in ("themeColor", "themeTint", "themeShade"):
        key = qn("w:" + attr)
        if key in color.attrib:
            del color.attrib[key]
'''
if "_force_black" not in t:
    t = t.replace("def setup_styles(doc: Document) -> None:", add + "\n\ndef setup_styles(doc: Document) -> None:", 1)

t = t.replace('''        s.font.color.rgb = RGBColor(0, 0, 0)''',
              '''        s.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(s.element.rPr)''')
t = t.replace('''        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(0, 0, 0)''',
              '''        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(r._element.get_or_add_rPr())''')
t = t.replace('''        r.font.size = Pt({1: 14, 2: 12, 3: 12}[min(level, 3)])
        r.font.color.rgb = RGBColor(0, 0, 0)''',
              '''        r.font.size = Pt({1: 14, 2: 12, 3: 12}[min(level, 3)])
        r.font.color.rgb = RGBColor(0, 0, 0)
        _force_black(r._element.get_or_add_rPr())''')
io.open(GEN, "w", encoding="utf-8", newline="\n").write(t)
print("生成器已加入 themeColor 清理:", t.count("_force_black"))
