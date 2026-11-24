#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""困难归因数据集评测：12 条样本（4 脚本 / 4 环境 / 4 缺陷），三模型对照。"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import (SYS_TRIAGE, Settings, build_backend, evaluate_triage,
                    user_triage)

BASE = os.path.dirname(os.path.abspath(__file__))
LOGS = json.load(open(os.path.join(BASE, "data", "failure_logs_hard.json"), encoding="utf-8"))
MODELS = [("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
          ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
          ("qwen-plus", "Qwen-Plus")]
LABELS = ["脚本问题", "环境问题", "系统缺陷"]

# 载入 .env
env = os.path.join(BASE, ".env")
if os.path.exists(env):
    for line in open(env, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

rows = []
for model, label in MODELS:
    s = Settings(provider="dashscope", model=model, max_tokens=8000).resolve()
    backend = build_backend(s)
    print(f"\n===== {label} =====")
    per = []
    for item in LOGS:
        raw = backend.complete(SYS_TRIAGE, user_triage(item))
        m = evaluate_triage(raw, item["gold"])
        cat = m["category"]
        per.append({"id": item["id"], "gold": item["gold"], "got": cat, "match": m["match"],
                    "raw": raw[:300]})
        flag = "OK " if m["match"] else "XX "
        print(f"  {flag}{item['id']:<5} gold={item['gold']:<5} got={cat or '空'}")
    acc = sum(1 for p in per if p["match"]) / len(per) * 100
    rows.append({"model": label, "accuracy": round(acc, 1), "detail": per})

# 混淆矩阵
print("\n===== 混淆矩阵（行=真实，列=预测）=====")
summary = {}
for r in rows:
    mat = {g: {p: 0 for p in LABELS + ["其他/空"]} for g in LABELS}
    for d in r["detail"]:
        got = d["got"] if d["got"] in LABELS else "其他/空"
        mat[d["gold"]][got] += 1
    summary[r["model"]] = {"accuracy": r["accuracy"], "matrix": mat}
    print(f"\n{r['model']}（准确率 {r['accuracy']}%）")
    print("           预测 脚本  环境  缺陷  其他")
    for g in LABELS:
        print(f"  真实 {g:<4}{mat[g]['脚本问题']:>5}{mat[g]['环境问题']:>6}{mat[g]['系统缺陷']:>6}{mat[g]['其他/空']:>6}")

# 错误扣缺陷率：真实非缺陷却被判成系统缺陷
for r in rows:
    wrong_defect = sum(1 for d in r["detail"] if d["gold"] != "系统缺陷" and d["got"] == "系统缺陷")
    recall_defect = sum(1 for d in r["detail"] if d["gold"] == "系统缺陷"
                        and (d["got"] == "系统缺陷") or (d["got"] in ("系统缺陷",) ))
    print(f"{r['model']:<22} 误判为缺陷 {wrong_defect} 次")

out = os.path.join(BASE, "outputs", "triage-hard.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"rows": rows, "summary": summary}, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n已写入", out)
