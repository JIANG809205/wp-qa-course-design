# -*- coding: utf-8 -*-
"""修图标记粘连、图号重号、补插 perf-chain。"""

import io
import re

P = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
t = io.open(P, encoding="utf-8").read()

# 1) 把粘连在标记后的正文拆到下一行
t = re.sub(r"(\[\[图:[A-Za-z0-9\-]+\|[^\]]+\]\])(?!\s*$)(?=\S)", r"\1\n\n", t, flags=re.M)

# 2) 图 4.x 重编号：拓扑 4.1、站点 4.2、后台 4.3
t = t.replace("[[图:site|图4.1 被测站点首页]]", "[[图:site|图4.2 被测站点首页]]")
t = t.replace("[[图:admin|图4.2 后台仪表盘界面]]", "[[图:admin|图4.3 后台仪表盘界面]]")

# 3) 补插 perf-chain（放在优化建议之前）
anchor = "据实测数据给出的优化方向是"
if "[[图:perf-chain" not in t and anchor in t:
    t = t.replace(anchor,
                  "[[图:perf-chain|图5.19 性能压测链路与观测点]]\n\n" + anchor, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("标记数:", t.count("[[图:"))
for ln in t.splitlines():
    if ln.strip().startswith("[[图:"):
        if not re.fullmatch(r"\[\[图:[A-Za-z0-9\-]+\|[^\]]+\]\]", ln.strip()):
            print("仍粘连:", ln[:60])
