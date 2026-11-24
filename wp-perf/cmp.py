import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
fp = font_manager.FontProperties(fname=FONT)
plt.rcParams["font.family"] = fp.get_name()
plt.rcParams["axes.unicode_minus"] = False
font_manager.fontManager.addfont(FONT)

def tps(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8", errors="replace")))
    ts = [int(r["timeStamp"]) for r in rows]
    return len(rows) / max(max(ts) - min(ts), 1) * 1000

root = "/mnt/e/软件质量保证与测试课程设计/wp-perf"
series = [("基线", f"{root}/results/home-100.jtl"),
          ("参数调优", f"{root}/results-tuned/home-100.jtl"),
          ("页面缓存", f"{root}/results-cache/home-100.jtl")]

labels, vals, colors = [], [], ["#4472C4", "#ED7D31", "#A5A5A5"]
for lab, p in series:
    if os.path.exists(p):
        labels.append(lab); vals.append(tps(p))

plt.figure(figsize=(6.5, 4.2))
bars = plt.bar(labels, vals, color=colors, width=0.5)
for b, v in zip(bars, vals):
    plt.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom",
             fontsize=10, fontproperties=fp)
plt.ylabel("TPS（100 并发）", fontproperties=fp)
plt.title("首页吞吐：优化前后对比", fontproperties=fp)
plt.xticks(fontproperties=fp)
plt.ylim(0, max(vals) * 1.25)
plt.tight_layout()
out = f"{root}/charts/optimization-compare.png"
plt.savefig(out, dpi=150)
print("saved", out, [round(v, 1) for v in vals])