# -*- coding: utf-8 -*-
"""逐条核验：报告里的每个数字 vs 原始数据重算结果。"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
import statistics

import openpyxl

ROOT = r"E:\软件质量保证与测试课程设计"
WSL = lambda p: p  # 路径已在 WorkBuddy 侧可见

results: list[tuple[str, str, str, bool]] = []


def check(name: str, claimed, actual, tol=0.15) -> None:
    if isinstance(claimed, (int, float)) and isinstance(actual, (int, float)):
        ok = abs(claimed - actual) <= tol
    else:
        ok = str(claimed) == str(actual)
    results.append((name, str(claimed), str(actual), ok))


# ---------- 1. 用例 ----------
wb = openpyxl.load_workbook(os.path.join(ROOT, "05-测试用例-核心40条.xlsx"))
ws = wb["测试用例"]
dist = {}
for r in range(2, ws.max_row + 1):
    v = ws.cell(row=r, column=10).value or "未执行"
    dist[v] = dist.get(v, 0) + 1
check("用例总数", 43, ws.max_row - 1, 0)
check("通过数", 39, dist.get("通过", 0), 0)
check("失败数", 4, dist.get("失败", 0), 0)

# ---------- 2. 缺陷 ----------
md = open(os.path.join(ROOT, "defect-hunt", "缺陷清单.md"), encoding="utf-8").read()
p1 = len(re.findall(r"## DEF-\d+.*?（P1）", md))
p2 = len(re.findall(r"## DEF-\d+.*?（P2）", md))
p3 = len(re.findall(r"## DEF-\d+.*?（P3）", md))
obs = len(re.findall(r"## DEF-\d+.*?观察项", md))
check("P1 缺陷数", 2, p1, 0)
check("P2 缺陷数", 5, p2, 0)
check("P3 缺陷数", 4, p3, 0)
check("观察项数", 1, obs, 0)

# ---------- 3. 权限矩阵 ----------
reps = []
for i in (1, 2, 3):
    p = os.path.join(ROOT, "defect-hunt", "matrix-reps", f"rep{i}.json")
    if os.path.exists(p):
        reps.append(json.load(open(p, encoding="utf-8")))
same = 0
for idx in range(len(reps[0])):
    vals = {json.dumps(r[idx]["api"]) for r in reps}
    if len(vals) == 1:
        same += 1
check("权限格数", 36, len(reps[0]), 0)
check("三次一致的格数", 36, same, 0)
check("权限矩阵重复次数", 3, len(reps), 0)

# ---------- 4. 兼容性（Chrome 12 组 + Firefox 12 组 = 24 组） ----------
compat_chrome = json.load(open(os.path.join(ROOT, "wp-compat", "compat.json"), encoding="utf-8"))
compat_ff = json.load(open(os.path.join(ROOT, "wp-compat", "firefox", "compat-firefox.json"), encoding="utf-8"))
compat = compat_chrome + compat_ff
check("兼容性组数", 24, len(compat), 0)
check("兼容性通过组数", 24, sum(1 for c in compat if c["pass"]), 0)

# ---------- 5. 性能（稳态口径：剔除前 10 秒爬坡） ----------
def jtl(path, ramp_ms=10000):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    t0 = min(int(r["timeStamp"]) for r in rows)
    t1 = max(int(r["timeStamp"]) for r in rows)
    steady = [r for r in rows if int(r["timeStamp"]) >= t0 + ramp_ms]
    el = sorted(float(r["elapsed"]) for r in steady)
    dur = max((t1 - (t0 + ramp_ms)) / 1000, 1)
    return len(steady) / dur, el[max(int(round(0.95 * len(el))) - 1, 0)]


def perf(directory: str, prefix: str):
    out = {}
    for t in (10, 50, 100):
        fs = sorted(glob.glob(os.path.join(ROOT, "wp-perf", directory, f"{prefix}-{t}-rep*.jtl")))
        if not fs:
            continue
        ms = [jtl(f) for f in fs]
        out[t] = (round(statistics.median(m[0] for m in ms), 1),
                  round(statistics.median(m[1] for m in ms)))
    return out


home = perf("results-rigor", "home")
blog = perf("results-rigor-blog", "list")

for t, claim in ((10, 129.8), (50, 127.8), (100, 127.2)):
    check(f"首页 {t} 并发 TPS", claim, home.get(t, (0, 0))[0], 0.6)
for t, claim in ((10, 102.9), (50, 88.4), (100, 55.1)):
    check(f"列表页 {t} 并发 TPS", claim, blog.get(t, (0, 0))[0], 0.6)
for t, claim in ((50, 526), (100, 1061)):
    check(f"首页 {t} 并发 P95", claim, home.get(t, (0, 0))[1], 3)
for t, claim in ((10, 147), (50, 783), (100, 2834)):
    check(f"列表页 {t} 并发 P95", claim, blog.get(t, (0, 0))[1], 3)

# ---------- 6. 大模型 ----------
flash = json.load(open(os.path.join(ROOT, "llm-qa", "outputs", "rigor",
                                    "summary-deepseek-v4.1-flash.json"), encoding="utf-8"))[0]
check("Flash 严格合规均值", 95.6, round(flash["strict_mean"], 1), 0.2)
check("Flash 合规 CI", 8.0, round(flash["strict_ci"], 1), 0.2)
check("Flash 需求覆盖", 96.2, round(flash["coverage_mean"], 1), 0.2)

for name, f, claim_cases, claim_cov in (
        ("Pro", "score-DeepSeek-V4-Pro.json", 196, 96.2),
        ("Qwen", "score-Qwen-Plus.json", 196, 93.6)):
    p = os.path.join(ROOT, "llm-qa", "outputs", f)
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        check(f"{name} 用例数", claim_cases, d["cases"], 0)
        check(f"{name} 需求覆盖", claim_cov, d["coverage"], 0.3)

dom = json.load(open(os.path.join(ROOT, "llm-qa", "outputs", "selector-fidelity-s96.json"),
                     encoding="utf-8"))
_rows = dom["rows"] if isinstance(dom, dict) else dom
_NAME = {"deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
         "deepseek-v4-pro": "DeepSeek-V4-Pro",
         "qwen-plus": "Qwen-Plus"}
rates = {_NAME.get(r["model"], r["model"]): r["fidelity"] for r in _rows}
for model, claim in (("DeepSeek-V4.1-Flash", 29.0), ("DeepSeek-V4-Pro", 33.1), ("Qwen-Plus", 34.9)):
    check(f"{model} 定位器保真", claim, rates.get(model, -1), 0.2)

strict = json.load(open(os.path.join(ROOT, "llm-qa", "outputs", "scripts96-summary.json"),
                        encoding="utf-8"))
NAME_MAP = {"deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
            "deepseek-v4-pro": "DeepSeek-V4-Pro",
            "qwen-plus": "Qwen-Plus"}
sr = {NAME_MAP.get(r["model"], r["model"]): r for r in strict}
for model, claim in (("DeepSeek-V4.1-Flash", 5.2), ("DeepSeek-V4-Pro", 1.0), ("Qwen-Plus", 0.0)):
    check(f"{model} 严格可运行", claim, sr[model]["strict_rate"], 0.1)

tri = json.load(open(os.path.join(ROOT, "llm-qa", "outputs", "triage24-summary.json"),
                     encoding="utf-8"))
tm = {r["model"]: r["accuracy"] for r in tri}
for model, claim in (("DeepSeek-V4.1-Flash", 95.8), ("DeepSeek-V4-Pro", 91.7), ("Qwen-Plus", 91.7)):
    check(f"{model} 归因准确率", claim, tm.get(model, -1), 0.1)

# ---------- 7. 双版本 ----------
fv = json.load(open(os.path.join(ROOT, "defect-hunt", "findings-versions.json"), encoding="utf-8"))
check("7.1.5 探针命中", 11, sum(1 for v in fv.get("7.1.5", {}).values() if v), 0)
check("7.1.4 探针命中", 11, sum(1 for v in fv.get("7.1.4", {}).values() if v), 0)

# ---------- 输出 ----------
ok = sum(1 for r in results if r[3])
print(f"{'核验项':<34}{'报告值':>12}{'重算值':>12}  判定")
print("-" * 72)
for name, claim, actual, good in results:
    print(f"{name:<34}{claim:>12}{actual:>12}  {'✅' if good else '❌ 不一致'}")
print("-" * 72)
print(f"共 {len(results)} 项，通过 {ok} 项，不一致 {len(results)-ok} 项")

json.dump([{"item": n, "claimed": c, "actual": a, "ok": o} for n, c, a, o in results],
          open(os.path.join(ROOT, "核验结果.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
