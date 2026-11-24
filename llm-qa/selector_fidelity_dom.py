#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用真实 DOM 的 id / name / class 全集校验定位器（n=20 脚本）。

CSS 选择器按"其中出现的 #id 与 .class 是否都真实存在"判定。
"""

from __future__ import annotations

import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOM = json.load(open(os.path.join(BASE, "data", "dom-ids.json"), encoding="utf-8"))
REAL_IDS = set(DOM["ids"])
REAL_NAMES = set(DOM["names"])
REAL_CLASSES = set(DOM.get("classes", []))

if not REAL_CLASSES:
    raise SystemExit("dom-ids.json 里没有 classes，请先重跑 collect_dom_ids.py")

DIRS = {"DeepSeek-V4.1-Flash": "/opt/qa/scripts20-deepseek-v4.1-flash/deepseek-v4.1-flash",
        "DeepSeek-V4-Pro": "/opt/qa/scripts20-deepseek-v4-pro/deepseek-v4-pro",
        "Qwen-Plus": "/opt/qa/scripts20-qwen-plus/qwen-plus"}

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')
XPATH_PAT = re.compile(r'By\.xpath\(\s*"([^"]+)"\s*\)')


def css_ok(css: str) -> bool:
    ids = re.findall(r"#([A-Za-z0-9_-]+)", css)
    classes = re.findall(r"\.([A-Za-z0-9_-]+)", css)
    if not ids and not classes:
        return False  # 纯标签选择器不参与判定，按未验证处理
    if any(i not in REAL_IDS for i in ids):
        return False
    if any(c not in REAL_CLASSES for c in classes):
        return False
    return True


rows = []
for label, d in DIRS.items():
    total = real = 0
    kind = {"id": [0, 0], "name": [0, 0], "css": [0, 0], "xpath": [0, 0]}
    files = sorted(glob.glob(os.path.join(d, "*.java")))
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        for i in ID_PAT.findall(code):
            total += 1
            kind["id"][0] += 1
            if i in REAL_IDS:
                real += 1
                kind["id"][1] += 1
        for n in NAME_PAT.findall(code):
            total += 1
            kind["name"][0] += 1
            if n in REAL_NAMES or n in REAL_IDS:
                real += 1
                kind["name"][1] += 1
        for css in CSS_PAT.findall(code):
            total += 1
            kind["css"][0] += 1
            if css_ok(css):
                real += 1
                kind["css"][1] += 1
        for xp in XPATH_PAT.findall(code):
            total += 1
            kind["xpath"][0] += 1
            found = re.findall(r"@id=['\"]([^'\"]+)['\"]", xp)
            if found and all(i in REAL_IDS for i in found):
                real += 1
                kind["xpath"][1] += 1
    rate = round(real / total * 100, 1) if total else 0
    rows.append({"model": label, "scripts": len(files), "selectors": total,
                 "real": real, "fidelity": rate, "by_kind": kind})
    detail = "  ".join(f"{k}:{v[1]}/{v[0]}" for k, v in kind.items() if v[0])
    print(f"{label:<22} 脚本 {len(files):>2}，定位器 {total:>3}，命中 {real:>3} → {rate:>5.1f}%   [{detail}]")

out = os.path.join(BASE, "outputs", "selector-fidelity-dom.json")
json.dump({"rows": rows,
           "real_ids": len(REAL_IDS), "real_names": len(REAL_NAMES),
           "real_classes": len(REAL_CLASSES)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n校验基准：id {len(REAL_IDS)} / name {len(REAL_NAMES)} / class {len(REAL_CLASSES)}")
print("已写入", out)
