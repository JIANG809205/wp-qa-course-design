#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只跑归因任务：24 条平衡样本（8/8/8）× 3 模型，输出准确率与混淆矩阵。"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import SYS_TRIAGE, Settings, build_backend, evaluate_triage, user_triage

BASE = os.path.dirname(os.path.abspath(__file__))
TRIAGE = json.load(open(os.path.join(BASE, "data", "triage24.json"), encoding="utf-8"))
OUT = os.environ.get("RIGOR_OUT", "/opt/qa/rigor-triage")
os.makedirs(OUT, exist_ok=True)

MODELS = [("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
          ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
          ("qwen-plus", "Qwen-Plus")]
LABELS = ["脚本问题", "环境问题", "系统缺陷"]

ENV = os.path.join(BASE, ".env")
if os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

print("样本分布:", dict(Counter(x["gold"] for x in TRIAGE)))

summary = []
for model, label in MODELS:
    backend = build_backend(Settings(provider="dashscope", model=model, max_tokens=6000).resolve())
    detail, ok, wrong = [], 0, 0
    for item in TRIAGE:
        raw = backend.complete(SYS_TRIAGE, user_triage(item))
        m = evaluate_triage(raw, item["gold"])
        ok += 1 if m["match"] else 0
        if item["gold"] != "系统缺陷" and m["category"] == "系统缺陷":
            wrong += 1
        detail.append({"id": item["id"], "gold": item["gold"], "got": m["category"],
                       "match": bool(m["match"])})
    mat = {g: {p: 0 for p in LABELS + ["其他"]} for g in LABELS}
    for d in detail:
        mat[d["gold"]][d["got"] if d["got"] in LABELS else "其他"] += 1
    row = {"model": label, "n": len(detail), "accuracy": round(ok / len(detail) * 100, 1),
           "wrong_defect": wrong, "matrix": mat, "detail": detail}
    summary.append(row)
    print(f"{label:<22} 准确率 {row['accuracy']:>5.1f}%  误判缺陷 {wrong}", flush=True)

json.dump(summary, open(os.path.join(OUT, "triage24-summary.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("已写入", os.path.join(OUT, "triage24-summary.json"))
