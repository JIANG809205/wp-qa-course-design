#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三模型对照：同一批任务分别跑 DeepSeek / DeepSeek-R1 / Qwen，汇总指标。

用法：python compare.py
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

MODELS = [
    ("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
    ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
    ("qwen-plus", "Qwen-Plus"),
]

ROWS = []


def run_one(model: str, out_dir: str) -> dict | None:
    cmd = [sys.executable, "run.py", "--provider", "dashscope",
           "--model", model, "--task", "all", "--out", out_dir, "--max-tokens", "6000"]
    print(f"\n========== {model} ==========")
    proc = subprocess.run(cmd, cwd=BASE)
    metrics = os.path.join(out_dir, "metrics.json")
    if proc.returncode != 0 or not os.path.exists(metrics):
        print(f"[失败] {model} 未产出 metrics.json")
        return None
    with open(metrics, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    results = {}
    for model, label in MODELS:
        safe = model.replace("/", "_")
        out_dir = os.path.join(BASE, "outputs", f"cmp-{safe}")
        data = run_one(model, out_dir)
        results[label] = data

    rows = []
    for label, data in results.items():
        if not data:
            rows.append({"模型": label, "用例数": "-", "合法JSON": "-", "字段完整": "-",
                         "与人工重合": "-", "脚本结构OK": "-", "含断言": "-",
                         "归因准确率": "-", "误判为缺陷": "-"})
            continue
        c = data.get("cases", {})
        s = data.get("scripts", {})
        t = data.get("triage", {})
        rows.append({
            "模型": label,
            "用例数": c.get("generated_cases", 0),
            "合法JSON": f"{c.get('valid_json_rate', 0)}%",
            "字段完整": f"{c.get('field_complete_rate', 0)}%",
            "与人工重合": f"{c.get('human_overlap_rate', 0)}%",
            "脚本结构OK": f"{s.get('syntax_ok_rate', 0)}%",
            "含断言": f"{s.get('assert_rate', 0)}%",
            "归因准确率": f"{t.get('accuracy', 0)}%",
            "误判为缺陷": t.get("hallucination_to_defect", 0),
        })

    cols = ["模型", "用例数", "合法JSON", "字段完整", "与人工重合",
            "脚本结构OK", "含断言", "归因准确率", "误判为缺陷"]

    out_csv = os.path.join(BASE, "outputs", "comparison.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print("\n================ 三模型对照 ================")
    widths = [max(len(str(r[c])) for r in rows + [dict(zip(cols, cols))]) for c in cols]
    for r in [dict(zip(cols, cols))] + rows:
        print("  ".join(str(r[c]).ljust(widths[i]) for i, c in enumerate(cols)))
    print(f"\n已写入 {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
