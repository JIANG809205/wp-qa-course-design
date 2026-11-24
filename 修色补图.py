# -*- coding: utf-8 -*-
"""把标题颜色改为黑色，并补充剩余截图。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"
t = io.open(P, encoding="utf-8").read()

t = t.replace("from docx.shared import Cm, Pt\n",
              "from docx.shared import Cm, Pt, RGBColor\n")

# 标题样式颜色
t = t.replace("""        s.font.bold = True
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")""",
              """        s.font.bold = True
        s.font.color.rgb = RGBColor(0, 0, 0)
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")""")

# 标题运行颜色
t = t.replace("""        r.font.size = Pt(18)""",
              """        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(0, 0, 0)""")
t = t.replace("""        r.font.size = Pt({1: 14, 2: 12, 3: 12}[min(level, 3)])""",
              """        r.font.size = Pt({1: 14, 2: 12, 3: 12}[min(level, 3)])
        r.font.color.rgb = RGBColor(0, 0, 0)""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("已改标题颜色:", t.count("RGBColor"))

# 正文补图：环境截图、上传目录证据
MD = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
m = io.open(MD, encoding="utf-8").read()

if "[[图:site" not in m:
    m = m.replace("这些配置均记录在环境脚本中，可一键重建。",
                  "这些配置均记录在环境脚本中，可一键重建。测试站点的首页如下图所示。\n\n"
                  "[[图:site|图5.1 被测站点首页（WP-QA-Lab 测试环境）]]\n\n"
                  "后台仪表盘与文章列表界面如下图所示。\n\n"
                  "[[图:admin|图5.2 后台仪表盘界面]]")

if "[[图:uploads" not in m:
    m = m.replace("24 组全部通过，横向溢出均为 0。",
                  "[[图:uploads|图6.8 DEF-003 证据：上传目录可浏览]]\n\n24 组全部通过，横向溢出均为 0。")

io.open(MD, "w", encoding="utf-8", newline="\n").write(m)
print("图标记数:", m.count("[[图:"))
