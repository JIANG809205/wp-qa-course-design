#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接从生成的 java 文件重算全部指标（不依赖 records.jsonl，避免分片竞争丢失记录）。"""

from __future__ import annotations

import glob
import json
import math
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOM = json.load(open(os.path.join(BASE, "data", "dom-ids.json"), encoding="utf-8"))
REAL_IDS, REAL_NAMES, REAL_CLASSES = set(DOM["ids"]), set(DOM["names"]), set(DOM["classes"])

CLASS_RE = re.compile(r"\bclass\s+\w+")
ASSERT_RE = re.compile(r"\bAssert\.\w+")
ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')

DIRS = {"deepseek-v4.1-flash": "/opt/qa/s96-deepseek-v4.1-flash/java",
        "deepseek-v4-pro": "/opt/qa/s96-deepseek-v4-pro/java",
        "qwen-plus": "/opt/qa/s96-qwen-plus/java"}


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0, (c - h) * 100), 1), round(min(100, (c + h) * 100), 1)


rows = []
for model, d in DIRS.items():
    files = sorted(glob.glob(os.path.join(d, "*.java")))
    n = len(files)
    stat = {"class": 0, "url": 0, "assert": 0, "sel_ok": 0, "struct": 0, "strict": 0}
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        body = re.sub(r"(?<!:)//[^\n]*", "", code)
        cid = os.path.basename(f).replace(".java", "")
        is_api = "API" in cid

        sels = []
        for i in ID_PAT.findall(body):
            sels.append(i in REAL_IDS)
        for nm in NAME_PAT.findall(body):
            sels.append(nm in REAL_NAMES or nm in REAL_IDS)
        for css in CSS_PAT.findall(body):
            ids = re.findall(r"#([A-Za-z0-9_-]+)", css)
            cls = re.findall(r"\.([A-Za-z0-9_-]+)", css)
            sels.append(bool(ids or cls) and all(i in REAL_IDS for i in ids)
                        and all(c in REAL_CLASSES for c in cls))

        has_class = bool(CLASS_RE.search(body))
        url_ok = ("localhost:8080" in body) and ("example.com" not in body)
        has_assert = bool(ASSERT_RE.search(body))
        sel_ok = all(sels) if is_api else (bool(sels) and all(sels))

        stat["class"] += has_class
        stat["url"] += url_ok
        stat["assert"] += has_assert
        stat["sel_ok"] += sel_ok
        st = has_class and url_ok and has_assert
        stat["struct"] += st
        stat["strict"] += st and sel_ok

    lo_s, hi_s = wilson(stat["struct"], n)
    lo_t, hi_t = wilson(stat["strict"], n)
    rows.append({
        "model": model, "n": n,
        "struct_k": stat["struct"], "struct_rate": round(stat["struct"] / n * 100, 1),
        "struct_ci": [lo_s, hi_s],
        "strict_k": stat["strict"], "strict_rate": round(stat["strict"] / n * 100, 1),
        "strict_ci": [lo_t, hi_t],
        "class_rate": round(stat["class"] / n * 100, 1),
        "url_rate": round(stat["url"] / n * 100, 1),
        "assert_rate": round(stat["assert"] / n * 100, 1),
        "selector_rate": round(stat["sel_ok"] / n * 100, 1),
    })

order = {"deepseek-v4.1-flash": 0, "deepseek-v4-pro": 1, "qwen-plus": 2}
rows.sort(key=lambda r: order.get(r["model"], 9))

print(f"{'模型':<24}{'n':>4}{'结构可运行':>14}{'严格可运行':>16}{'有类':>7}{'URL对':>7}{'断言':>7}{'定位器':>7}")
for r in rows:
    s_txt = str(r["struct_k"]) + "/" + str(r["n"])
    t_txt = str(r["strict_k"]) + "/" + str(r["n"])
    print(f"{r['model']:<24}{r['n']:>4}{s_txt:>14}{t_txt:>16}"
          f"{r['class_rate']:>7.0f}%{r['url_rate']:>7.0f}%{r['assert_rate']:>7.0f}%{r['selector_rate']:>7.0f}%")
    print(f"{'':24}{'':4}CI(结构) {r['struct_ci']}  CI(严格) {r['strict_ci']}")

out = os.path.join(BASE, "outputs", "scripts96-summary.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已写入", out)
