#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用严谨版数据重画全部图表（覆盖旧图，避免新旧矛盾）。"""

from __future__ import annotations

import csv
import glob
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "charts-new")
os.makedirs(OUT, exist_ok=True)

# 中文字体
for cand in ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
             "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
             "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

C1, C2, C3 = "#2E5C8A", "#C0504D", "#9BBB59"


def jtl_metrics(path: str):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    if not rows:
        return None
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000
    n = len(rows)
    err = sum(1 for r in rows if str(r["success"]).lower() != "true")
    return {"tps": n / dur, "p95": el[int(0.95 * n) - 1], "err": err * 100 / n}


def series(pattern: str, threads=(10, 50, 100)):
    out = {}
    for t in threads:
        files = sorted(glob.glob(pattern.format(t=t)))
        vals = [jtl_metrics(f) for f in files]
        vals = [v for v in vals if v]
        if vals:
            out[t] = {
                "tps": statistics.median(v["tps"] for v in vals),
                "tps_all": [v["tps"] for v in vals],
                "p95": statistics.median(v["p95"] for v in vals),
                "err": statistics.mean(v["err"] for v in vals),
            }
    return out


home = series(os.path.join(BASE, "results-rigor", "home-{t}-rep*.jtl"))
lst = series(os.path.join(BASE, "results-rigor-blog", "list-{t}-rep*.jtl"))

# ---------- 图 1：TPS 对比 ----------
fig, ax = plt.subplots(figsize=(8, 5))
xs = [10, 50, 100]
for data, label, color, marker in ((home, "静态首页", C1, "o"), (lst, "文章列表页", C2, "s")):
    ys = [data[t]["tps"] for t in xs if t in data]
    err = []
    for t in xs:
        if t in data:
            v = data[t]["tps_all"]
            err.append((max(v) - min(v)) / 2 if len(v) > 1 else 0)
    ax.errorbar([t for t in xs if t in data], ys, yerr=err, label=label,
                color=color, marker=marker, capsize=4, linewidth=2)
ax.set_xlabel("并发用户数")
ax.set_ylabel("吞吐量 TPS")
ax.set_title("吞吐量随并发变化（60 秒稳态 × 3 次取中位数）")
ax.set_xticks(xs)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-tps.png"), dpi=160)
plt.close(fig)

# ---------- 图 2：P95 ----------
fig, ax = plt.subplots(figsize=(8, 5))
for data, label, color, marker in ((home, "静态首页", C1, "o"), (lst, "文章列表页", C2, "s")):
    ax.plot([t for t in xs if t in data], [data[t]["p95"] for t in xs if t in data],
            label=label, color=color, marker=marker, linewidth=2)
ax.axhline(2000, color="gray", linestyle="--", linewidth=1)
ax.text(10, 2050, "2 秒不可接受线", color="gray", fontsize=9)
ax.set_xlabel("并发用户数")
ax.set_ylabel("P95 响应时间 (ms)")
ax.set_title("P95 响应时间随并发变化")
ax.set_xticks(xs)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-p95.png"), dpi=160)
plt.close(fig)

# ---------- 图 3：CPU ----------
fig, ax = plt.subplots(figsize=(8, 5))
for name, sub, color in (("静态首页", "results-rigor", C1), ("文章列表页", "results-rigor-blog", C2)):
    cpu_file = os.path.join(BASE, sub, "cpu.csv")
    if not os.path.exists(cpu_file):
        continue
    rows = list(csv.reader(open(cpu_file, encoding="utf-8")))
    by_t = {}
    for r in rows:
        if len(r) >= 3:
            by_t.setdefault(int(r[0]), []).append(float(r[2]))
    ts = sorted(by_t)
    ax.plot(ts, [statistics.mean(by_t[t]) for t in ts], marker="o",
            label=name, color=color, linewidth=2)
ax.axhline(800, color="gray", linestyle="--", linewidth=1)
ax.text(10, 810, "8 核上限", color="gray", fontsize=9)
ax.set_xlabel("并发用户数")
ax.set_ylabel("容器 CPU 使用率 (%)")
ax.set_title("压测期间的容器 CPU（8 核）")
ax.set_xticks([10, 50, 100])
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-cpu.png"), dpi=160)
plt.close(fig)

# ---------- 图 4：定位器保真度三阶段收敛 ----------
stages = ["3 条脚本\n(手写基准)", "10 条脚本\n(手写基准)", "20 条脚本\n(真实 DOM)"]
vals = {"DeepSeek-V4.1-Flash": [36.4, 52.0, 21.1],
        "DeepSeek-V4-Pro": [30.0, 45.8, 24.4],
        "Qwen-Plus": [57.1, 47.8, 25.0]}
fig, ax = plt.subplots(figsize=(8, 5))
for (name, ys), color in zip(vals.items(), (C1, C2, C3)):
    ax.plot(stages, ys, marker="o", label=name, color=color, linewidth=2)
ax.set_ylabel("定位器保真度 (%)")
ax.set_title("定位器保真度：两次修正后收敛到 21%–25%")
ax.grid(alpha=0.3)
ax.legend()
ax.set_ylim(0, 70)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "llm-fidelity.png"), dpi=160)
plt.close(fig)

# ---------- 图 5：结构可运行 vs 严格可运行 ----------
strict = json.load(open(os.path.join(BASE, "..", "llm-qa", "outputs", "runnable-strict.json"),
                        encoding="utf-8"))
models = [r["model"] for r in strict]
fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(models))
ax.bar([i - 0.2 for i in x], [r["struct_rate"] for r in strict], width=0.4,
       label="结构可运行（有类+URL对+有断言）", color=C1)
ax.bar([i + 0.2 for i in x], [r["strict_rate"] for r in strict], width=0.4,
       label="严格可运行（定位器全真实）", color=C2)
ax.set_xticks(list(x))
ax.set_xticklabels(models, fontsize=9)
ax.set_ylabel("可运行率 (%)")
ax.set_title("结构合格 ≠ 能跑：两者的差距就是定位器幻觉")
ax.grid(axis="y", alpha=0.3)
ax.legend(fontsize=9)
for i, r in enumerate(strict):
    ax.text(i - 0.2, r["struct_rate"] + 1.5, f'{r["struct_rate"]:.0f}%', ha="center", fontsize=9)
    ax.text(i + 0.2, r["strict_rate"] + 1.5, f'{r["strict_rate"]:.0f}%', ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "llm-runnable.png"), dpi=160)
plt.close(fig)

# ---------- 图 6：缺陷等级分布 ----------
fig, ax = plt.subplots(figsize=(6, 5))
levels = ["P1 严重", "P2 一般", "P3 轻微", "观察项"]
counts = [2, 5, 4, 1]
colors = [C2, "#E8A33D", C3, "#999999"]
bars = ax.bar(levels, counts, color=colors)
for b, c in zip(bars, counts):
    ax.text(b.get_x() + b.get_width() / 2, c + 0.1, str(c), ha="center", fontsize=11)
ax.set_ylabel("数量")
ax.set_title("缺陷等级分布（共 11 条 + 1 观察项）")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "defects.png"), dpi=160)
plt.close(fig)

print("已生成图表：")
for f in sorted(glob.glob(os.path.join(OUT, "*.png"))):
    print(f"  {os.path.basename(f)}  {os.path.getsize(f)//1024} KB")
print("\n静态首页:", {t: round(v['tps'], 1) for t, v in home.items()})
print("列表页  :", {t: round(v['tps'], 1) for t, v in lst.items()})
