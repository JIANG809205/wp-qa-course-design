#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 96 条脚本上重算定位器保真度（真实 DOM 基准）。"""

from __future__ import annotations

import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOM = json.load(open(os.path.join(BASE, "data", "dom-ids.json"), encoding="utf-8"))
REAL_IDS, REAL_NAMES, REAL_CLASSES = set(DOM["ids"]), set(DOM["names"]), set(DOM["classes"])

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')
XPATH_PAT = re.compile(r'By\.xpath\(\s*"([^"]+)"\s*\)')

rows = []
for d in sorted(glob.glob("/opt/qa/s96-*")):
    java = os.path.join(d, "java")
    files = sorted(glob.glob(os.path.join(java, "*.java")))
    if not files:
        continue
    total = real = 0
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        for i in ID_PAT.findall(code):
            total += 1
            real += i in REAL_IDS
        for n in NAME_PAT.findall(code):
            total += 1
            real += (n in REAL_NAMES or n in REAL_IDS)
        for css in CSS_PAT.findall(code):
            ids = re.findall(r"#([A-Za-z0-9_-]+)", css)
            cls = re.findall(r"\.([A-Za-z0-9_-]+)", css)
            total += 1
            if (ids or cls) and all(i in REAL_IDS for i in ids) and all(c in REAL_CLASSES for c in cls):
                real += 1
        for xp in XPATH_PAT.findall(code):
            found = re.findall(r"@id=['\"]([^'\"]+)['\"]", xp)
            total += 1
            if found and all(i in REAL_IDS for i in found):
                real += 1
    rate = round(real / total * 100, 1) if total else 0.0
    model = os.path.basename(d).replace("s96-", "")
    rows.append({"model": model, "scripts": len(files), "selectors": total,
                 "real": real, "fidelity": rate})
    print(f"{model:<24} 脚本 {len(files):>3}  定位器 {total:>4}  命中 {real:>4} → {rate:>5.1f}%")

out = os.path.join(BASE, "outputs", "selector-fidelity-s96.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已写入", out)
