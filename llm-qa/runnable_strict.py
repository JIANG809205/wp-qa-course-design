#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""严格可运行率：类声明 + URL 正确 + 有断言 + 所有定位器真实存在。

对比"结构可运行"（不校验定位器）与"严格可运行"，说明两者差距。
"""

from __future__ import annotations

import glob
import json
import math
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOM = json.load(open(os.path.join(BASE, "data", "dom-ids.json"), encoding="utf-8"))
REAL_IDS, REAL_NAMES, REAL_CLASSES = set(DOM["ids"]), set(DOM["names"]), set(DOM["classes"])

DIRS = {"DeepSeek-V4.1-Flash": "/opt/qa/scripts20-deepseek-v4.1-flash/deepseek-v4.1-flash",
        "DeepSeek-V4-Pro": "/opt/qa/scripts20-deepseek-v4-pro/deepseek-v4-pro",
        "Qwen-Plus": "/opt/qa/scripts20-qwen-plus/qwen-plus"}

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')
XPATH_PAT = re.compile(r'By\.xpath\(\s*"([^"]+)"\s*\)')
CLASS_RE = re.compile(r"\bclass\s+\w+")
ASSERT_RE = re.compile(r"\bAssert\.\w+")


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, (c - h) * 100), min(100.0, (c + h) * 100)


def selectors_of(code):
    out = []
    for i in ID_PAT.findall(code):
        out.append(("id", i in REAL_IDS))
    for n in NAME_PAT.findall(code):
        out.append(("name", n in REAL_NAMES or n in REAL_IDS))
    for css in CSS_PAT.findall(code):
        ids = re.findall(r"#([A-Za-z0-9_-]+)", css)
        cls = re.findall(r"\.([A-Za-z0-9_-]+)", css)
        ok = bool(ids or cls) and all(i in REAL_IDS for i in ids) and all(c in REAL_CLASSES for c in cls)
        out.append(("css", ok))
    for xp in XPATH_PAT.findall(code):
        found = re.findall(r"@id=['\"]([^'\"]+)['\"]", xp)
        out.append(("xpath", bool(found) and all(i in REAL_IDS for i in found)))
    return out


rows = []
for label, d in DIRS.items():
    files = sorted(glob.glob(os.path.join(d, "*.java")))
    struct_ok = strict_ok = 0
    details = []
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        body = re.sub(r"(?<!:)//[^\n]*", "", code)
        has_class = bool(CLASS_RE.search(body))
        url_ok = ("localhost:8080" in body or "BASE_URL" in body) and "example.com" not in body
        has_assert = bool(ASSERT_RE.search(body))
        sels = selectors_of(body)
        fname = os.path.basename(f)
        is_api = fname.startswith("TC-API")
        # 接口类用例不需要 UI 定位器；UI 类用例必须至少有一个且全部真实
        if is_api:
            all_real = all(ok for _, ok in sels)
        else:
            all_real = bool(sels) and all(ok for _, ok in sels)
        struct = has_class and url_ok and has_assert
        struct_ok += struct
        strict_ok += struct and all_real
        details.append({"file": os.path.basename(f), "struct": struct,
                        "selectors": len(sels), "all_real": all_real})
    n = len(files)
    lo, hi = wilson(strict_ok, n)
    rows.append({"model": label, "n": n, "struct_ok": struct_ok, "strict_ok": strict_ok,
                 "struct_rate": round(struct_ok / n * 100, 1),
                 "strict_rate": round(strict_ok / n * 100, 1),
                 "strict_ci": [round(lo, 1), round(hi, 1)], "detail": details})
    print(f"{label:<22} n={n}  结构可运行 {struct_ok}/{n} = {struct_ok/n*100:>5.1f}%   "
          f"严格可运行 {strict_ok}/{n} = {strict_ok/n*100:>5.1f}%  CI [{lo:.0f}%, {hi:.0f}%]")

out = os.path.join(BASE, "outputs", "runnable-strict.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已写入", out)
