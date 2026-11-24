#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""96 条脚本样本评测（支持断点续跑，输出到 ext4）。"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import SYS_SCRIPTS, Settings, build_backend, strip_fences, user_scripts
from evaluate_v2 import assertion_strength, url_correct

BASE = os.path.dirname(os.path.abspath(__file__))
SPECS = json.load(open(os.path.join(BASE, "data", "scripts96.json"), encoding="utf-8"))

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--outdir", required=True)
args = ap.parse_args()

os.makedirs(args.outdir, exist_ok=True)
JAVA_DIR = os.path.join(args.outdir, "java")
os.makedirs(JAVA_DIR, exist_ok=True)
RESULT = os.path.join(args.outdir, "records.jsonl")

ENV = os.path.join(BASE, ".env")
if os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

CLASS_RE = re.compile(r"\bclass\s+\w+")
ASSERT_RE = re.compile(r"\bAssert\.\w+")
ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')
DOM = json.load(open(os.path.join(BASE, "data", "dom-ids.json"), encoding="utf-8"))
REAL_IDS, REAL_NAMES, REAL_CLASSES = set(DOM["ids"]), set(DOM["names"]), set(DOM["classes"])


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0, (c - h) * 100), 1), round(min(100, (c + h) * 100), 1)


def selectors_ok(body: str, is_api: bool):
    sels = []
    for i in ID_PAT.findall(body):
        sels.append(i in REAL_IDS)
    for n in NAME_PAT.findall(body):
        sels.append(n in REAL_NAMES or n in REAL_IDS)
    for css in CSS_PAT.findall(body):
        ids = re.findall(r"#([A-Za-z0-9_-]+)", css)
        cls = re.findall(r"\.([A-Za-z0-9_-]+)", css)
        sels.append(bool(ids or cls) and all(i in REAL_IDS for i in ids)
                    and all(c in REAL_CLASSES for c in cls))
    if is_api:
        return all(sels) if sels else True
    return bool(sels) and all(sels)


backend = build_backend(Settings(provider="dashscope", model=args.model, max_tokens=6000).resolve())
done = 0
for spec in SPECS:
    out_java = os.path.join(JAVA_DIR, f"{spec['id']}.java")
    if os.path.exists(out_java) and os.path.getsize(out_java) > 50:
        done += 1
        continue
    for attempt in range(3):
        try:
            code = strip_fences(backend.complete(SYS_SCRIPTS, user_scripts(spec)))
            break
        except Exception as e:  # noqa: BLE001
            print(f"  {spec['id']} 第 {attempt+1} 次失败: {type(e).__name__}", flush=True)
            time.sleep(3)
    else:
        continue
    open(out_java, "w", encoding="utf-8").write(code)
    body = re.sub(r"(?<!:)//[^\n]*", "", code)
    is_api = "API" in spec["id"]
    rec = {
        "id": spec["id"],
        "has_class": bool(CLASS_RE.search(body)),
        "url_ok": url_correct(code),
        "has_assert": bool(ASSERT_RE.search(body)),
        "selectors_ok": selectors_ok(body, is_api),
        "chars": len(code),
    }
    rec["struct_ok"] = rec["has_class"] and rec["url_ok"] and rec["has_assert"]
    rec["strict_ok"] = rec["struct_ok"] and rec["selectors_ok"]
    with open(RESULT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    done += 1
    if done % 10 == 0:
        print(f"  进度 {done}/96", flush=True)

recs = [json.loads(l) for l in open(RESULT, encoding="utf-8") if l.strip()]
n = len(recs)
k_s = sum(1 for r in recs if r["struct_ok"])
k_t = sum(1 for r in recs if r["strict_ok"])
lo_s, hi_s = wilson(k_s, n)
lo_t, hi_t = wilson(k_t, n)
summary = {
    "model": args.model, "n": n,
    "struct_k": k_s, "struct_rate": round(k_s / n * 100, 1), "struct_ci": [lo_s, hi_s],
    "strict_k": k_t, "strict_rate": round(k_t / n * 100, 1), "strict_ci": [lo_t, hi_t],
    "class_rate": round(sum(1 for r in recs if r["has_class"]) / n * 100, 1),
    "url_rate": round(sum(1 for r in recs if r["url_ok"]) / n * 100, 1),
    "assert_rate": round(sum(1 for r in recs if r["has_assert"]) / n * 100, 1),
    "selector_rate": round(sum(1 for r in recs if r["selectors_ok"]) / n * 100, 1),
}
json.dump(summary, open(os.path.join(args.outdir, "summary.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"\n{args.model}: n={n}  结构可运行 {k_s} ({summary['struct_rate']}% CI {summary['struct_ci']})  "
      f"严格可运行 {k_t} ({summary['strict_rate']}% CI {summary['strict_ci']})")
