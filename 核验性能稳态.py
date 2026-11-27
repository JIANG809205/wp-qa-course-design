# -*- coding: utf-8 -*-
"""用稳态口径（剔除前 10 秒爬坡）重算性能，核对报告表 5.5 / 5.6。"""

from __future__ import annotations

import csv
import glob
import os
import statistics

BASE = r"E:\软件质量保证与测试课程设计\wp-perf"


def metrics(path: str, warmup_ms: int = 10000):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    if not rows:
        return None
    ts = [int(r["timeStamp"]) for r in rows]
    t0, t1 = min(ts), max(ts)
    # 稳态窗口：跳过开头 10 秒
    steady = [r for r in rows if int(r["timeStamp"]) >= t0 + warmup_ms]
    if len(steady) < 10:
        steady = rows
    el = sorted(float(r["elapsed"]) for r in steady)
    dur = (t1 - (t0 + warmup_ms)) / 1000
    n = len(steady)
    err = sum(1 for r in steady if str(r["success"]).lower() != "true")
    p95 = el[max(0, int(0.95 * n) - 1)]
    return {"tps": n / dur if dur > 0 else 0, "avg": statistics.mean(el), "p95": p95,
            "err": err * 100 / n, "n": n}


def report(directory: str, prefix: str, label: str):
    print(f"\n=== {label}（稳态口径）===")
    print(f"{'并发':<6}{'TPS中位':>10}{'三次':>26}{'平均RT':>9}{'P95':>9}{'错误率':>8}")
    for t in (10, 50, 100):
        files = sorted(glob.glob(os.path.join(BASE, directory, f"{prefix}-{t}-rep*.jtl")))
        if not files:
            print(f"{t:<6} 无数据")
            continue
        ms = [metrics(f) for f in files]
        ms = [m for m in ms if m]
        tps = [m["tps"] for m in ms]
        p95 = [m["p95"] for m in ms]
        print(f"{t:<6}{statistics.median(tps):>10.1f}"
              f"{'  ' + ' / '.join(f'{v:.1f}' for v in tps):>26}"
              f"{statistics.mean([m['avg'] for m in ms]):>9.0f}"
              f"{statistics.median(p95):>9.0f}"
              f"{statistics.mean([m['err'] for m in ms]):>7.1f}%")


report("results-rigor", "home", "静态首页")
report("results-rigor-blog", "list", "文章列表页")
