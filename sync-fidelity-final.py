# -*- coding: utf-8 -*-
"""同步 metrics-v2.csv 的保真度列，并在方法依据文档中补充 DOM 基准说明。"""

import csv
import io
import json
import os

BASE = r"E:\软件质量保证与测试课程设计\llm-qa"

dom = json.load(open(os.path.join(BASE, "outputs", "selector-fidelity-dom.json"), encoding="utf-8"))
rates = {r["model"]: r["fidelity"] for r in dom["rows"]}

csv_path = os.path.join(BASE, "outputs", "metrics-v2.csv")
rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
for r in rows:
    if r["模型"] in rates:
        r["定位器保真度"] = f"{rates[r['模型']]}%"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("CSV 保真度:", [(r["模型"], r["定位器保真度"]) for r in rows])

md = os.path.join(BASE, "评测方法依据.md")
t = io.open(md, encoding="utf-8").read()
add = """
---

## 六、定位器保真度的基准集（本项目的关键修正）

文献中的"元素精确率"通常以**真实页面元素集**为基准。本项目最初用**手写的 22 个 id** 作基准，导致保真度被高估（30%–57%）。改为用 Selenium 登录后逐页抓取 **9 个后台页面**的完整属性集：

| 基准 | 数量 |
|---|---|
| 元素 id | 1181 |
| 表单 name | 193 |
| CSS class | 769 |

据此重算后，三模型（20 条脚本）定位器保真度为 **21.1% / 24.4% / 25.0%**，即**四分之三以上定位器在真实页面上不存在**。这与文献中"标准 LLM 元素解析率约 40%"的观察方向一致（本项目更低，因为脚本未提供 DOM 上下文）。

脚本：`collect_dom_ids.py`（抓基准）、`selector_fidelity_dom.py`（比对）。
"""
if "六、定位器保真度的基准集" not in t:
    io.open(md, "w", encoding="utf-8", newline="\n").write(t.rstrip() + "\n" + add)
    print("已追加基准说明")
else:
    print("已存在基准说明")
