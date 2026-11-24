# -*- coding: utf-8 -*-
"""合并三模型 96 条脚本结果（含 Wilson CI），输出 CSV 与表。"""

import csv
import glob
import json
import math
import os

BASE = r"E:\软件质量保证与测试课程设计\llm-qa"


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0, (c - h) * 100), 1), round(min(100, (c + h) * 100), 1)


rows = []
for f in sorted(glob.glob("/opt/qa/s96-*/summary.json")):
    d = json.load(open(f, encoding="utf-8"))
    lo, hi = wilson(d["strict_k"], d["n"])
    rows.append({
        "model": d["model"], "n": d["n"],
        "struct_k": d["struct_k"], "struct_rate": d["struct_rate"],
        "strict_k": d["strict_k"], "strict_rate": d["strict_rate"],
        "strict_ci": [lo, hi],
        "class_rate": d["class_rate"], "url_rate": d["url_rate"],
        "assert_rate": d["assert_rate"], "selector_rate": d["selector_rate"],
    })

if not rows:
    raise SystemExit("还没有 96 条结果")

order = {"deepseek-v4.1-flash": 0, "deepseek-v4-pro": 1, "qwen-plus": 2}
rows.sort(key=lambda r: order.get(r["model"], 9))

print(f"{'模型':<24}{'n':>4}{'结构可运行':>14}{'严格可运行':>14}{'严格 95% CI':>20}{'定位器合格':>10}")
for r in rows:
    lo, hi = r["strict_ci"]
    print(f"{r['model']:<24}{r['n']:>4}{r['struct_k']:>6}/{r['n']:<4}"
          f"{r['strict_k']:>8}/{r['n']:<4}{f'[{lo:.1f}%, {hi:.1f}%]':>20}{r['selector_rate']:>9.1f}%")

out_json = os.path.join(BASE, "outputs", "scripts96-summary.json")
json.dump(rows, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

out_csv = os.path.join(BASE, "outputs", "scripts96-summary.csv")
with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["模型", "n", "结构可运行k", "结构可运行率", "严格可运行k", "严格可运行率",
                "严格CI下限", "严格CI上限", "有类声明率", "URL正确率", "含断言率", "定位器合格率"])
    for r in rows:
        lo, hi = r["strict_ci"]
        w.writerow([r["model"], r["n"], r["struct_k"], f"{r['struct_rate']}%",
                    r["strict_k"], f"{r['strict_rate']}%", f"{lo}%", f"{hi}%",
                    f"{r['class_rate']}%", f"{r['url_rate']}%", f"{r['assert_rate']}%",
                    f"{r['selector_rate']}%"])

print(f"\n已写入 {out_json}\n已写入 {out_csv}")
