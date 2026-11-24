#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精美版图表：统一配色、数值标注、阈值线、网格与留白。"""

from __future__ import annotations

import csv
import glob
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Patch

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(BASE, "charts-final")
os.makedirs(OUT, exist_ok=True)

# ---- 字体 ----
for cand in ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
             "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"):
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break
plt.rcParams.update({
    "axes.unicode_minus": False,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "axes.edgecolor": "#666666",
    "axes.linewidth": 0.8,
    "axes.titlesize": 13,
    "axes.labelsize": 10.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9,
    "legend.frameon": False,
})

NAVY, RED, ORANGE, GREEN, GRAY = "#1F4E79", "#C00000", "#ED7D31", "#548235", "#7F7F7F"


def style(ax, ygrid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ygrid:
        ax.yaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.45)
    ax.set_axisbelow(True)


# ---------------- 性能数据 ----------------
def jtl(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000
    return len(rows) / dur, el[int(0.95 * len(rows)) - 1]


def series(directory, prefix):
    out = {}
    for t in (10, 50, 100):
        fs = sorted(glob.glob(os.path.join(BASE, directory, f"{prefix}-{t}-rep*.jtl")))
        if not fs:
            continue
        ms = [jtl(f) for f in fs]
        tps = [m[0] for m in ms]
        out[t] = {"tps": statistics.median(tps), "lo": min(tps), "hi": max(tps),
                  "p95": statistics.median(m[1] for m in ms)}
    return out


home = series("results-rigor", "home")
blog = series("results-rigor-blog", "list")
XS = [10, 50, 100]


def cpu_of(sub):
    p = os.path.join(BASE, sub, "cpu.csv")
    if not os.path.exists(p):
        return {}
    acc = {}
    for row in csv.reader(open(p, encoding="utf-8")):
        if len(row) >= 3:
            acc.setdefault(int(row[0]), []).append(float(row[2]))
    return {k: statistics.mean(v) for k, v in acc.items()}


cpu_home = cpu_of("results-rigor")
cpu_blog = cpu_of("results-rigor-blog")

# ---------------- 图 1：TPS ----------------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for data, label, color, marker in ((home, "静态首页", NAVY, "o"), (blog, "文章列表页", RED, "s")):
    xs = [t for t in XS if t in data]
    ys = [data[t]["tps"] for t in xs]
    err = [[data[t]["tps"] - data[t]["lo"] for t in xs], [data[t]["hi"] - data[t]["tps"] for t in xs]]
    ax.errorbar(xs, ys, yerr=err, label=label, color=color, marker=marker,
                markersize=6, linewidth=2, capsize=4, capthick=1.2)
    dy = 11 if label == "静态首页" else -18
    for x, y in zip(xs, ys):
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, dy),
                    ha="center", fontsize=8.5, color=color)
ax.axvspan(50, 100, color=RED, alpha=0.04)
ax.set_xticks(XS)
ax.set_xlabel("并发用户数")
ax.set_ylabel("吞吐量（TPS）")
ax.set_title("吞吐量随并发变化（60 秒稳态 × 3 次取中位数）", pad=10)
ax.set_ylim(35, 152)
style(ax)
ax.legend(loc="lower left", ncol=1)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-tps.png"))
plt.close(fig)

# ---------------- 图 2：P95 ----------------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for data, label, color, marker in ((home, "静态首页", NAVY, "o"), (blog, "文章列表页", RED, "s")):
    xs = [t for t in XS if t in data]
    ax.plot(xs, [data[t]["p95"] for t in xs], label=label, color=color,
            marker=marker, markersize=6, linewidth=2)
    for t in xs:
        ax.annotate(f"{data[t]['p95']:.0f}", (t, data[t]["p95"]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8.5, color=color)
ax.axhline(1000, color=GRAY, linestyle=":", linewidth=1)
ax.text(11, 1040, "1 秒", color=GRAY, fontsize=8.5)
ax.axhline(2000, color=RED, linestyle="--", linewidth=1)
ax.text(11, 2040, "2 秒（不可接受）", color=RED, fontsize=8.5)
ax.set_xticks(XS)
ax.set_xlabel("并发用户数")
ax.set_ylabel("P95 响应时间（ms）")
ax.set_title("P95 响应时间：列表页在 100 并发突破 2 秒", pad=10)
style(ax)
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-p95.png"))
plt.close(fig)

# ---------------- 图 3：CPU ----------------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
w = 3.4
xs = np.arange(len(XS))
h1 = [cpu_home.get(t, 0) for t in XS]
h2 = [cpu_blog.get(t, 0) for t in XS]
b1 = ax.bar(xs - 0.19, h1, width=0.36, label="静态首页", color=NAVY)
b2 = ax.bar(xs + 0.19, h2, width=0.36, label="文章列表页", color=RED)
for bars in (b1, b2):
    for b in bars:
        ax.annotate(f"{b.get_height():.0f}%", (b.get_x() + b.get_width() / 2, b.get_height()),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
ax.axhline(800, color=GRAY, linestyle="--", linewidth=1)
ax.text(-0.45, 815, "8 核上限", color=GRAY, fontsize=8.5)
ax.set_xticks(xs)
ax.set_xticklabels([f"{t} 并发" for t in XS])
ax.set_ylim(0, 880)
ax.set_ylabel("容器 CPU 使用率（%）")
ax.set_title("压测期间容器 CPU：稳定占用 6–6.8 核", pad=10)
style(ax)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "perf-cpu.png"))
plt.close(fig)

# ---------------- 图 4：定位器保真度三阶段 ----------------
stages = ["3 条脚本\n手写基准", "10 条脚本\n手写基准", "20 条脚本\n真实 DOM"]
vals = {"DeepSeek-V4.1-Flash": ([36.4, 52.0, 21.1], NAVY, "o"),
        "DeepSeek-V4-Pro": ([30.0, 45.8, 24.4], ORANGE, "^"),
        "Qwen-Plus": ([57.1, 47.8, 25.0], GREEN, "D")}
fig, ax = plt.subplots(figsize=(7.4, 4.6))
for name, (ys, color, marker) in vals.items():
    ax.plot(stages, ys, marker=marker, markersize=6, linewidth=2, color=color, label=name)
    for i, y in enumerate(ys):
        ax.annotate(f"{y:.1f}", (i, y), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=color)
ax.axhspan(21, 25, color=NAVY, alpha=0.06)
ax.set_ylabel("定位器保真度（%）")
ax.set_title("定位器保真度：两次修正后收敛到 21%–25%", pad=10)
ax.set_ylim(0, 68)
style(ax)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "llm-fidelity.png"))
plt.close(fig)

# ---------------- 图 5：结构可运行 vs 严格可运行 ----------------
strict = json.load(open(os.path.join(ROOT, "llm-qa", "outputs", "runnable-strict.json"),
                        encoding="utf-8"))
models = [r["model"] for r in strict]
short = ["Flash", "Pro", "Qwen"]
xs = np.arange(len(models))
fig, ax = plt.subplots(figsize=(7.2, 4.6))
b1 = ax.bar(xs - 0.19, [r["struct_rate"] for r in strict], width=0.36,
            label="结构可运行（类+URL+断言）", color="#8FAADC")
b2 = ax.bar(xs + 0.19, [r["strict_rate"] for r in strict], width=0.36,
            label="严格可运行（定位器全部真实）", color=RED)
for bars, key in ((b1, "struct_rate"), (b2, "strict_rate")):
    for b, r in zip(bars, strict):
        ax.annotate(f"{r[key]:.0f}%", (b.get_x() + b.get_width() / 2, b.get_height()),
                    textcoords="offset points", xytext=(0, 3), ha="center", fontsize=9)
# 置信区间（严格）
for i, r in enumerate(strict):
    lo, hi = r["strict_ci"]
    ax.plot([i + 0.19, i + 0.19], [lo, hi], color="#7F0000", linewidth=1.2)
    ax.plot([i + 0.13, i + 0.25], [lo, lo], color="#7F0000", linewidth=1.2)
    ax.plot([i + 0.13, i + 0.25], [hi, hi], color="#7F0000", linewidth=1.2)
ax.set_xticks(xs)
ax.set_xticklabels(["DeepSeek-V4.1-Flash", "DeepSeek-V4-Pro", "Qwen-Plus"])
ax.set_ylim(0, 82)
ax.set_ylabel("可运行率（%）")
ax.set_title("结构合格 ≠ 能跑：差距即定位器幻觉（n=20，误差线为 95% CI）", pad=10)
style(ax)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "llm-runnable.png"))
plt.close(fig)

# ---------------- 图 6：缺陷分布（横向） ----------------
levels = ["P1 严重", "P2 一般", "P3 轻微"]
counts = [2, 5, 4]
colors = [RED, ORANGE, "#BFBF00"]
fig, ax = plt.subplots(figsize=(6.8, 3.4))
bars = ax.barh(levels, counts, color=colors, height=0.55)
for b, c in zip(bars, counts):
    ax.annotate(f"{c} 条  ({c/11*100:.0f}%)", (c, b.get_y() + b.get_height() / 2),
                textcoords="offset points", xytext=(6, -3), fontsize=9)
ax.set_xlim(0, 7)
ax.set_xlabel("缺陷数量")
ax.set_title("缺陷等级分布（共 11 条，另有 1 条观察项）", pad=10)
style(ax, ygrid=False)
ax.xaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.45)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "defects.png"))
plt.close(fig)

# ---------------- 图 7：模块执行分布（堆叠） ----------------
modules = ["登录", "内容", "媒体", "评论", "接口", "权限", "设置", "主题插件", "兼容性"]
passed = [3, 8, 3, 5, 5, 5, 3, 3, 3]
failed = [2, 0, 2, 0, 1, 0, 0, 0, 0]
fig, ax = plt.subplots(figsize=(7.6, 4.2))
xs = np.arange(len(modules))
ax.bar(xs, passed, color=GREEN, label="通过")
ax.bar(xs, failed, bottom=passed, color=RED, label="失败")
for i, (p, f) in enumerate(zip(passed, failed)):
    ax.text(i, p + f + 0.15, str(p + f), ha="center", fontsize=8.5)
ax.set_xticks(xs)
ax.set_xticklabels(modules, fontsize=9)
ax.set_ylabel("用例数")
ax.set_ylim(0, 10)
ax.set_title("各模块用例执行结果（43 条，失败 4 条集中在登录/媒体/接口）", pad=10)
style(ax)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "cases-by-module.png"))
plt.close(fig)

# ---------------- 图 8：权限矩阵热力图 ----------------
roles = ["管理员", "编辑", "作者", "投稿者", "订阅者"]
ops = ["发布文章", "编辑他人", "审核评论", "上传媒体", "新建用户", "修改设置"]
# 1=允许 0.5=有条件 0=拒绝
matrix = np.array([
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0],
    [0.5, 0, 0, 1, 0, 0],
    [0.5, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
])
fig, ax = plt.subplots(figsize=(7.2, 4.0))
cmap = matplotlib.colors.ListedColormap(["#F4B6B6", "#FFE699", "#C6E0B4"])
ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(ops)))
ax.set_xticklabels(ops, fontsize=9)
ax.set_yticks(range(len(roles)))
ax.set_yticklabels(roles, fontsize=9)
for i in range(len(roles)):
    for j in range(len(ops)):
        txt = {1: "允许", 0.5: "有条件", 0: "拒绝"}[matrix[i][j]]
        ax.text(j, i, txt, ha="center", va="center", fontsize=8.5)
ax.set_title("权限矩阵实测：30 格全部符合预期，0 越权（×3 次重复）", pad=10)
ax.set_xticks(np.arange(-0.5, len(ops), 1), minor=True)
ax.set_yticks(np.arange(-0.5, len(roles), 1), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="minor", length=0)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "permission-matrix.png"))
plt.close(fig)

print("生成图表：")
for f in sorted(glob.glob(os.path.join(OUT, "*.png"))):
    print(f"  {os.path.basename(f):<26}{os.path.getsize(f)//1024:>4} KB")
