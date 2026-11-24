#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总修正后的列表页数据（/qa-blog/，60 秒 × 3 次）。"""

from __future__ import annotations

import csv
import glob
import os
import statistics

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "results-rigor-blog")


def metrics(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000
    n = len(rows)
    err = sum(1 for r in rows if str(r["success"]).lower() != "true")
    return n / dur, statistics.mean(el), el[int(0.95 * n) - 1], err * 100 / n


print(f"{'并发':<6}{'TPS(中位)':>12}{'范围':>14}{'平均RT':>9}{'P95':>8}{'错误率':>8}{'样本数':>7}")
summary = {}
for t in (10, 50, 100):
    files = sorted(glob.glob(os.path.join(OUT, f"list-{t}-rep*.jtl")))
    if not files:
        print(f"{t:<6} 无数据")
        continue
    ms = [metrics(f) for f in files]
    tps = [m[0] for m in ms]
    p95 = [m[2] for m in ms]
    summary[t] = {"tps_median": round(statistics.median(tps), 1),
                  "tps_all": [round(v, 1) for v in tps],
                  "p95_median": round(statistics.median(p95), 0),
                  "rt": round(statistics.mean([m[1] for m in ms]), 0),
                  "err": round(statistics.mean([m[3] for m in ms]), 2),
                  "n": len(files)}
    s = summary[t]
    print(f"{t:<6}{s['tps_median']:>12.1f}{str(s['tps_all']):>14}{s['rt']:>9.0f}"
          f"{s['p95_median']:>8.0f}{s['err']:>7.2f}%{s['n']:>7}")

import json
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n已写入", os.path.join(OUT, "summary.json"))
