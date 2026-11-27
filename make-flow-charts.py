# -*- coding: utf-8 -*-
"""生成报告新增的四张示意图：总体流程、文章状态迁移、修复前后对照、缺陷流转。"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "wp-perf", "charts-final")
os.makedirs(OUT, exist_ok=True)

for cand in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"):
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#1F3864"
BLUE = "#2E5C8A"
LIGHT = "#DCE6F2"
GRAY = "#7F7F7F"
RED = "#C00000"
GREEN = "#2E7D32"
ORANGE = "#C55A11"


def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, fs=12, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                linewidth=1.1, facecolor=fc, edgecolor=ec, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color="#1F1F1F", zorder=3, fontweight="bold" if bold else "normal")


def arrow(ax, p1, p2, color=NAVY, style="-|>", ls="-", lw=1.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=12,
                                 color=color, linewidth=lw, linestyle=ls, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}"))


# ---------------- 图1 总体测试流程 ----------------
fig, ax = plt.subplots(figsize=(7.6, 3.9))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis("off")
box(ax, 0.2, 3.9, 2.0, 0.8, "需求分析\nR01–R10", fs=11)
box(ax, 2.6, 3.9, 2.0, 0.8, "测试计划\n准入/准出标准", fs=9.5)
box(ax, 5.0, 3.9, 2.0, 0.8, "用例设计\n等价类/边界/状态/判定表", fs=10.5)
box(ax, 7.4, 3.9, 2.2, 0.8, "环境与数据基线\n版本固定·1000 篇", fs=10.5)
box(ax, 7.4, 2.5, 2.2, 0.85, "执行\n功能·接口·权限\n性能·安全·兼容", fs=10.5)
box(ax, 4.9, 2.5, 2.0, 0.85, "缺陷登记\n11 条（分级）", fs=9.5)
box(ax, 2.5, 2.5, 1.9, 0.85, "准出判定\n8 项指标", fs=9.5)
box(ax, 0.2, 2.5, 1.8, 0.85, "修复与复测\n12 项探针回归", fs=10.5)
box(ax, 0.2, 1.2, 2.0, 0.8, "报告与图表", fs=9.5)
box(ax, 2.7, 1.2, 2.4, 0.8, "数据核验（41 项）\n脚本回溯原始文件", fs=10.5)
box(ax, 5.6, 1.2, 2.0, 0.8, "结论与遗留风险", fs=9.5)
arrow(ax, (2.2, 4.3), (2.6, 4.3))
arrow(ax, (4.6, 4.3), (5.0, 4.3))
arrow(ax, (7.0, 4.3), (7.4, 4.3))
arrow(ax, (8.5, 3.9), (8.5, 3.35))
arrow(ax, (7.4, 2.92), (6.9, 2.92))
arrow(ax, (4.9, 2.92), (4.4, 2.92))
arrow(ax, (2.5, 2.92), (2.0, 2.92))
arrow(ax, (1.1, 2.5), (1.1, 2.0))
arrow(ax, (2.2, 1.6), (2.7, 1.6))
arrow(ax, (5.1, 1.6), (5.6, 1.6))
arrow(ax, (1.1, 3.35), (5.6, 3.35), color=RED, ls="--", lw=1.0, rad=-0.12)
ax.text(2.6, 3.55, "不达标：修复后回归复测", fontsize=8, color=RED)
ax.text(5.0, 0.55, "任一环节的结论都必须能回溯到原始文件；数字由核验脚本统一比对",
        ha="center", fontsize=9, color=GRAY)
ax.set_title("本次测试的总体流程", fontsize=12, color=NAVY, pad=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "flow-test.png"), dpi=200, facecolor="white")
plt.close(fig)

# ---------------- 图2 文章状态迁移 ----------------
fig, ax = plt.subplots(figsize=(7.4, 3.4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.4)
ax.axis("off")
pos = {"draft": (0.6, 2.4), "pending": (3.0, 2.4), "publish": (5.4, 2.4), "trash": (7.9, 2.4)}
labels = {"draft": "草稿\ndraft", "pending": "待审\npending", "publish": "已发布\npublish", "trash": "回收站\ntrash"}
for k, (x, y) in pos.items():
    box(ax, x, y, 1.5, 0.9, labels[k], fs=10)
arrow(ax, (2.1, 2.85), (3.0, 2.85))
ax.text(2.25, 3.0, "提交审核", fontsize=8.5, color=NAVY)
arrow(ax, (4.5, 2.85), (5.4, 2.85))
ax.text(4.62, 3.0, "审核通过", fontsize=8.5, color=NAVY)
arrow(ax, (6.9, 2.85), (7.9, 2.85))
ax.text(7.0, 3.0, "移入回收站", fontsize=8.5, color=NAVY)
arrow(ax, (7.9, 2.6), (6.9, 2.6), ls="--", color=BLUE)
ax.text(7.05, 2.22, "还原", fontsize=8.5, color=BLUE)
arrow(ax, (3.0, 2.62), (2.1, 2.62), ls="--", color=BLUE)
ax.text(2.2, 2.2, "退回修改", fontsize=8.5, color=BLUE)
arrow(ax, (1.35, 3.3), (5.4, 3.55), color=RED, ls="--", rad=-0.25)
ax.text(2.4, 4.0, "投稿者直接发布：应被拒绝或降级为待审（TC-PERM-001）", fontsize=8.5, color=RED)
arrow(ax, (8.65, 2.4), (8.65, 1.55), color=ORANGE)
ax.text(8.75, 1.75, "永久删除", fontsize=8.5, color=ORANGE)
box(ax, 7.9, 0.55, 1.5, 0.75, "已删除", fc="#F2F2F2", ec=GRAY, fs=10)
ax.text(0.6, 1.2, "实线＝合法迁移　虚线＝回退路径　红色虚线＝非法迁移（越权）",
        fontsize=9, color=GRAY)
ax.set_title("文章状态迁移与合法/非法路径", fontsize=12, color=NAVY, pad=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "flow-state.png"), dpi=200, facecolor="white")
plt.close(fig)

# ---------------- 图3 修复前后对照 ----------------
b = json.load(open(os.path.join(ROOT, "hardening", "before.json"), encoding="utf-8"))
a = json.load(open(os.path.join(ROOT, "hardening", "after.json"), encoding="utf-8"))
items = b["items"]
n = len(items)
fig, ax = plt.subplots(figsize=(7.6, 4.9))
ax.set_xlim(0, 2)
ax.set_ylim(0, n + 0.6)
ax.axis("off")
ax.text(0.5, n + 0.25, "修复前", ha="center", fontsize=10.5, color=RED, fontweight="bold")
ax.text(1.5, n + 0.25, "修复后", ha="center", fontsize=10.5, color=GREEN, fontweight="bold")
for i, (x, y) in enumerate(zip(items, a["items"])):
    row = n - i - 0.5
    ax.text(-0.05, row, f"{x['id']} {x['name']}", ha="right", va="center", fontsize=8.6)
    for col, rec in ((0.5, x), (1.5, y)):
        hit = rec["hit"]
        ax.add_patch(Rectangle((col - 0.22, row - 0.3), 0.44, 0.6,
                               facecolor="#F4CCCC" if hit else "#D9EAD3",
                               edgecolor="white", linewidth=1.2))
        ax.text(col, row, "命中" if hit else "阻断", ha="center", va="center", fontsize=8.4,
                color=RED if hit else GREEN)
ax.plot([1.0, 1.0], [0.1, n + 0.05], color="#BFBFBF", linewidth=0.8)
ax.text(1.0, -0.35, f"命中数 {b['hits']}/{b['total']} → {a['hits']}/{a['total']}",
        ha="center", fontsize=10, color=NAVY, fontweight="bold")
ax.set_title("修复前后 12 项探针命中对比", fontsize=12, color=NAVY, pad=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fix-compare.png"), dpi=200, facecolor="white")
plt.close(fig)

# ---------------- 图4 缺陷状态流转 ----------------
fig, ax = plt.subplots(figsize=(8.8, 3.3))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.4)
ax.axis("off")
stages = [("登记", "11 条\nP1 2 / P2 5 / P3 4", 0.35), ("已修复", "10 条\n配置层加固", 2.75),
          ("复测通过", "10 条\n探针回归", 5.15), ("已关闭", "10 条\n关闭率 90.9%", 7.55)]
for title, sub, x in stages:
    box(ax, x, 1.5, 1.9, 1.0, f"{title}\n{sub}", fc=LIGHT, fs=9.5)
for i in range(3):
    arrow(ax, (stages[i][2] + 1.9, 2.0), (stages[i + 1][2], 2.0), lw=1.4)
box(ax, 7.55, 0.3, 1.9, 0.75, "遗留 1 条\nDEF-010（P3）", fc="#FCE4D6", ec=ORANGE, fs=10.5)
box(ax, 2.75, 0.3, 1.9, 0.75, "观察 1 条\nDEF-007 不作修复", fc="#F2F2F2", ec=GRAY, fs=10.5)
arrow(ax, (3.7, 0.68), (8.5, 0.68), color=ORANGE, ls=":", lw=1)
ax.text(6.0, 0.78, "转入遗留风险清单", fontsize=8.5, color=ORANGE, ha="center")
ax.set_title("缺陷状态流转与关闭率", fontsize=12, color=NAVY, pad=6)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "defect-flow.png"), dpi=200, facecolor="white")
plt.close(fig)

print("已生成：flow-test.png flow-state.png fix-compare.png defect-flow.png")
