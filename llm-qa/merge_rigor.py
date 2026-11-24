# -*- coding: utf-8 -*-
"""合并三个模型的严谨评测结果，输出表格与 CSV。"""

import csv
import glob
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "outputs", "rigor")

rows = []
for f in sorted(glob.glob(os.path.join(OUT, "summary-*.json"))):
    data = json.load(open(f, encoding="utf-8"))
    rows.extend(data)

if not rows:
    raise SystemExit("没有找到 summary-*.json，评测可能尚未完成")

order = {"DeepSeek-V4.1-Flash": 0, "DeepSeek-V4-Pro": 1, "Qwen-Plus": 2}
rows.sort(key=lambda r: order.get(r["model"], 9))

print(f"{'模型':<22}{'用例/次':>7}{'严格合规 均值±CI':>20}{'需求覆盖 均值±CI':>20}"
      f"{'可运行':>7}{'归因(n=24)':>11}{'误判缺陷':>8}")
for r in rows:
    print(f"{r['model']:<22}{r['cases_per_rep']:>7}"
          f"{r['strict_mean']:>13.1f}±{r['strict_ci']:<6.1f}"
          f"{r['coverage_mean']:>13.1f}±{r['coverage_ci']:<6.1f}"
          f"{r['runnable_rate']:>6.0f}%{r['triage_acc']:>10.1f}%{r['triage_wrong_defect']:>8}")

print("\n脚本维度明细")
print(f"{'模型':<22}{'有类声明':>9}{'URL正确':>9}{'有断言':>8}{'可运行':>8}")
for r in rows:
    print(f"{r['model']:<22}{r['class_rate']:>8.0f}%{r['url_ok_rate']:>8.0f}%"
          f"{r['assert_rate']:>7.0f}%{r['runnable_rate']:>7.0f}%")

print("\n各模型 3 次重复的原始值")
for r in rows:
    s = [f"{x['strict_rate']:.1f}" for x in r["reps"]]
    c = [f"{x['coverage']:.1f}" for x in r["reps"]]
    print(f"  {r['model']:<22} 严格合规 {s}  覆盖 {c}")

csv_path = os.path.join(OUT, "rigor-summary.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["模型", "每次用例数", "严格合规均值", "标准差", "95%CI", "需求覆盖均值",
                "标准差", "95%CI", "脚本可运行率", "归因准确率(n=24)", "误判为缺陷次数"])
    for r in rows:
        w.writerow([r["model"], r["cases_per_rep"], r["strict_mean"], r["strict_sd"],
                    r["strict_ci"], r["coverage_mean"], r["coverage_sd"], r["coverage_ci"],
                    r["runnable_rate"], r["triage_acc"], r["triage_wrong_defect"]])

print(f"\n已写入 {csv_path}")
