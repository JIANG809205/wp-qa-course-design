# -*- coding: utf-8 -*-
"""解析 JMeter jtl（CSV），产出指标汇总与图表。"""

import csv
import glob
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "charts")
os.makedirs(OUT, exist_ok=True)

# 中文字体（显式指定 TTC 文件，避免找不到字体导致方块）
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(FONT)
_CJK = font_manager.FontProperties(fname=FONT)
plt.rcParams["font.family"] = _CJK.get_name()
plt.rcParams["axes.unicode_minus"] = False


def load(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def metrics(rows, label_filter=None):
    if label_filter:
        rows = [r for r in rows if r.get("label") == label_filter]
    if not rows:
        return None
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000.0
    err = sum(1 for r in rows if str(r["success"]).lower() != "true")
    n = len(rows)

    def pct(p):
        k = max(int(round(p / 100.0 * n)) - 1, 0)
        return el[k]

    return {
        "samples": n,
        "duration_s": round(dur, 1),
        "tps": round(n / dur, 1),
        "avg_ms": round(statistics.mean(el), 0),
        "p95_ms": round(pct(95), 0),
        "p99_ms": round(pct(99), 0),
        "max_ms": round(max(el), 0),
        "errors": err,
        "err_rate": round(err * 100.0 / n, 2),
    }


SCEN = {
    "home": ("首页", "/", None),
    "detail": ("文章详情", "/?p=1002", None),
    "search": ("搜索结果页", "/?s=test", None),
    "admin": ("后台文章列表", "/wp-admin/edit.php", "GET edit.php"),
}

summary = []
for name, (title, path, label) in SCEN.items():
    for f in sorted(glob.glob(os.path.join(RES, f"{name}-*.jtl"))):
        threads = int(os.path.basename(f).split("-")[1].split(".")[0])
        m = metrics(load(f), label)
        if m:
            m.update({"scenario": title, "path": path, "threads": threads})
            summary.append(m)

cols = ["scenario", "path", "threads", "samples", "duration_s", "tps",
        "avg_ms", "p95_ms", "p99_ms", "max_ms", "errors", "err_rate"]
csv_path = os.path.join(ROOT, "summary.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in summary:
        w.writerow({k: r[k] for k in cols})
print("summary ->", csv_path)
for r in summary:
    print(f"{r['scenario']:<8} {r['threads']:>4}线程  样本={r['samples']:>5}  "
          f"TPS={r['tps']:>7}  平均={r['avg_ms']:>6}ms  P95={r['p95_ms']:>6}ms  "
          f"错误率={r['err_rate']}%")


def series(name, key):
    pts = sorted([r for r in summary if r["scenario"] == name and r["path"] != "/wp-admin/edit.php"],
                 key=lambda x: x["threads"])
    return [p["threads"] for p in pts], [p[key] for p in pts]


# 图1：TPS vs 并发
plt.figure(figsize=(8, 5))
for name in ("首页", "文章详情", "搜索结果页"):
    x, y = series(name, "tps")
    if x:
        plt.plot(x, y, marker="o", label=name)
plt.xlabel("并发线程数", fontproperties=_CJK)
plt.ylabel("TPS（每秒完成请求数）", fontproperties=_CJK)
plt.title("吞吐量随并发变化", fontproperties=_CJK)
plt.grid(alpha=0.3)
plt.legend(prop=_CJK)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "tps.png"), dpi=150)

# 图2：平均与 P95 响应时间
plt.figure(figsize=(8, 5))
for name in ("首页", "文章详情", "搜索结果页"):
    x, y = series(name, "avg_ms")
    if x:
        plt.plot(x, y, marker="o", label=f"{name} 平均")
    x, y = series(name, "p95_ms")
    if x:
        plt.plot(x, y, marker="s", linestyle="--", label=f"{name} P95")
plt.xlabel("并发线程数", fontproperties=_CJK)
plt.ylabel("响应时间（ms）", fontproperties=_CJK)
plt.title("响应时间随并发变化", fontproperties=_CJK)
plt.grid(alpha=0.3)
plt.legend(prop=_CJK, fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "response-time.png"), dpi=150)

# 图3：后台列表
adm = sorted([r for r in summary if r["path"] == "/wp-admin/edit.php"], key=lambda x: x["threads"])
if adm:
    x = [a["threads"] for a in adm]
    plt.figure(figsize=(6, 4))
    plt.bar([str(i) for i in x], [a["tps"] for a in adm], color="#4472C4", width=0.5)
    for i, a in enumerate(adm):
        plt.text(i, a["tps"], f"{a['tps']} TPS\n{a['avg_ms']:.0f}ms",
                 ha="center", va="bottom", fontsize=9, fontproperties=_CJK)
    plt.xlabel("并发线程数", fontproperties=_CJK)
    plt.ylabel("TPS")
    plt.title("后台文章列表（含登录）吞吐", fontproperties=_CJK)
    plt.ylim(0, max(a["tps"] for a in adm) * 1.35)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "admin.png"), dpi=150)

print("charts ->", OUT)
