#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐 Pro / Qwen 的脚本生成样本（10 条/模型），统一口径评分。"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import SYS_SCRIPTS, Settings, build_backend, strip_fences, user_scripts
from rigor_eval import SCRIPT_CASES
from evaluate_v2 import assertion_strength, url_correct

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR", "/opt/qa/scripts10")
os.makedirs(OUT, exist_ok=True)

MODELS = [("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
          ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
          ("qwen-plus", "Qwen-Plus")]

ENV = os.path.join(BASE, ".env")
if os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

CLASS_RE = re.compile(r"\bclass\s+\w+")
summary = []

for model, label in MODELS:
    backend = build_backend(Settings(provider="dashscope", model=model, max_tokens=6000).resolve())
    rows = []
    for case in SCRIPT_CASES:
        code = strip_fences(backend.complete(SYS_SCRIPTS, user_scripts(case)))
        path = os.path.join(OUT, model, f"{case['id']}.java")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(code)
        s = assertion_strength(code)
        rows.append({
            "id": case["id"],
            "has_class": bool(CLASS_RE.search(code)),
            "url_ok": url_correct(code),
            "asserts": s["asserts"],
            "runnable": bool(CLASS_RE.search(code)) and url_correct(code) and s["asserts"] > 0,
        })
    n = len(rows)
    row = {
        "model": label, "n": n,
        "class_rate": round(sum(r["has_class"] for r in rows) / n * 100, 1),
        "url_ok_rate": round(sum(r["url_ok"] for r in rows) / n * 100, 1),
        "assert_rate": round(sum(1 for r in rows if r["asserts"] > 0) / n * 100, 1),
        "runnable_rate": round(sum(1 for r in rows if r["runnable"]) / n * 100, 1),
        "detail": rows,
    }
    summary.append(row)
    print(f"{label:<22} 可运行 {row['runnable_rate']:>5.1f}%  URL正确 {row['url_ok_rate']:>5.1f}%  "
          f"有类 {row['class_rate']:>5.1f}%  有断言 {row['assert_rate']:>5.1f}%", flush=True)

json.dump(summary, open(os.path.join(OUT, "scripts10-summary.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("已写入", os.path.join(OUT, "scripts10-summary.json"))
