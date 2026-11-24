#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20 条脚本样本 + Wilson 95% 置信区间（对齐 arXiv 2601.06034 的报告方式）。"""

from __future__ import annotations

import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import SYS_SCRIPTS, Settings, build_backend, strip_fences, user_scripts
from rigor_eval import SCRIPT_CASES
from evaluate_v2 import assertion_strength, url_correct

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR", "/opt/qa/scripts20")
os.makedirs(OUT, exist_ok=True)

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--model", default="")
_args, _ = _ap.parse_known_args()
_MODELS_ALL = [("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
               ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
               ("qwen-plus", "Qwen-Plus")]
MODELS = [m for m in _MODELS_ALL if not _args.model or m[0] == _args.model]

ENV = os.path.join(BASE, ".env")
if os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

CLASS_RE = re.compile(r"\bclass\s+\w+")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, (centre - half) * 100), min(100.0, (centre + half) * 100)


summary = []
for model, label in MODELS:
    backend = build_backend(Settings(provider="dashscope", model=model, max_tokens=6000).resolve())
    rows = []
    for case in SCRIPT_CASES:
        code = strip_fences(backend.complete(SYS_SCRIPTS, user_scripts(case)))
        d = os.path.join(OUT, model)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, f"{case['id']}.java"), "w", encoding="utf-8").write(code)
        s = assertion_strength(code)
        has_class = bool(CLASS_RE.search(code))
        ok_url = url_correct(code)
        rows.append({"id": case["id"], "has_class": has_class, "url_ok": ok_url,
                     "asserts": s["asserts"],
                     "runnable": has_class and ok_url and s["asserts"] > 0})
    n = len(rows)
    k_run = sum(r["runnable"] for r in rows)
    k_url = sum(r["url_ok"] for r in rows)
    k_cls = sum(r["has_class"] for r in rows)
    lo, hi = wilson(k_run, n)
    row = {
        "model": label, "n": n,
        "class_rate": round(k_cls / n * 100, 1),
        "url_ok_rate": round(k_url / n * 100, 1),
        "assert_rate": round(sum(1 for r in rows if r["asserts"] > 0) / n * 100, 1),
        "runnable_k": k_run,
        "runnable_rate": round(k_run / n * 100, 1),
        "runnable_ci": [round(lo, 1), round(hi, 1)],
        "detail": rows,
    }
    summary.append(row)
    print(f"{label:<22} n={n}  可运行 {k_run}/{n} = {row['runnable_rate']}%  "
          f"Wilson 95% CI [{lo:.1f}%, {hi:.1f}%]  有类 {k_cls}/{n}  URL {k_url}/{n}", flush=True)

json.dump(summary, open(os.path.join(OUT, "scripts20-summary.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("已写入", os.path.join(OUT, "scripts20-summary.json"))
