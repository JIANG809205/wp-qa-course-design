# -*- coding: utf-8 -*-
"""合并三模型 20 条脚本结果，输出表格与 CSV（含 Wilson CI）。"""

import csv
import glob
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob("/opt/qa/scripts20-*/scripts20-summary.json")):
    rows.extend(json.load(open(f, encoding="utf-8")))

if not rows:
    raise SystemExit("还没有结果文件")

order = {"DeepSeek-V4.1-Flash": 0, "DeepSeek-V4-Pro": 1, "Qwen-Plus": 2}
rows.sort(key=lambda r: order.get(r["model"], 9))

print(f"{'模型':<22}{'n':>4}{'有类':>8}{'URL正确':>9}{'有断言':>8}{'可运行':>16}")
for r in rows:
    lo, hi = r["runnable_ci"]
    print(f"{r['model']:<22}{r['n']:>4}{r['class_rate']:>7.0f}%{r['url_ok_rate']:>8.0f}%"
          f"{r['assert_rate']:>7.0f}%{r['runnable_rate']:>8.0f}%  [{lo:.0f}%, {hi:.0f}%]")

out = os.path.join(BASE, "outputs", "scripts20-summary.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

csv_path = os.path.join(BASE, "outputs", "scripts20-summary.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["模型", "样本数n", "有类声明率", "URL正确率", "含断言率",
                "可运行数k", "可运行率", "Wilson95%CI下限", "Wilson95%CI上限"])
    for r in rows:
        lo, hi = r["runnable_ci"]
        w.writerow([r["model"], r["n"], f"{r['class_rate']}%", f"{r['url_ok_rate']}%",
                    f"{r['assert_rate']}%", r["runnable_k"], f"{r['runnable_rate']}%",
                    f"{lo}%", f"{hi}%"])

print(f"\n已写入 {out}\n已写入 {csv_path}")
