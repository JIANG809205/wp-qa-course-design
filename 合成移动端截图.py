# -*- coding: utf-8 -*-
"""把两张 375px 移动端截图并排拼成一张横版对比图（仅排版，不改截图内容）。"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import font_manager

ROOT = os.path.dirname(os.path.abspath(__file__))
SHOT = os.path.join(ROOT, "wp-compat", "screenshots")
for cand in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"):
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

pairs = [("mobile-375-admin.png", "后台文章列表"), ("mobile-375-blog.png", "博客列表页")]
fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.3), dpi=200)
for ax, (name, title) in zip(axes, pairs):
    img = mpimg.imread(os.path.join(SHOT, name))
    ax.imshow(img)
    ax.set_title(title + "（375×812）", fontsize=10.5, pad=6, fontweight="bold")
    ax.axis("off")
fig.tight_layout(pad=0.8)
out = os.path.join(SHOT, "mobile-pair.png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("已生成:", out)
