# -*- coding: utf-8 -*-
"""全项目数字一致性审查：把文档里的关键数字与"数据源"比对。"""

from __future__ import annotations

import glob
import json
import os
import re

import openpyxl

ROOT = r"E:\软件质量保证与测试课程设计"
issues: list[str] = []


def note(msg: str) -> None:
    issues.append(msg)
    print("  [!]", msg)


print("===== 1. 用例表 =====")
wb = openpyxl.load_workbook(os.path.join(ROOT, "05-测试用例-核心40条.xlsx"))
ws = wb["测试用例"]
total = ws.max_row - 1
dist = {}
for r in range(2, ws.max_row + 1):
    v = ws.cell(row=r, column=10).value or "未执行"
    dist[v] = dist.get(v, 0) + 1
print(f"  用例 {total} 条，{dist}")
if total != 43:
    note(f"用例数与文档声称的 43 不一致：{total}")

ws2 = wb["缺陷记录"]
defects = ws2.max_row - 1
print(f"  缺陷记录 {defects} 行（含观察项）")
if defects != 12:
    note(f"缺陷记录行数异常：{defects}")

print("\n===== 2. 大模型指标 =====")
flash = json.load(open(os.path.join(ROOT, "llm-qa/outputs/rigor/summary-deepseek-v4.1-flash.json"),
                      encoding="utf-8"))[0]
print(f"  Flash 严格合规 {flash['strict_mean']}±{flash['strict_ci']}，覆盖 {flash['coverage_mean']}")
if abs(flash["strict_mean"] - 95.6) > 0.2:
    note(f"Flash 严格合规与文档 95.6% 不符：{flash['strict_mean']}")

tri = json.load(open(os.path.join(ROOT, "llm-qa/outputs/triage24-summary.json"), encoding="utf-8"))
for r in tri:
    print(f"  归因 {r['model']}: {r['accuracy']}% (n={r['n']})")
    if r["n"] != 24:
        note(f"归因样本数不是 24：{r['model']} n={r['n']}")

print("\n===== 3. 脚本样本（10 vs 20） =====")
s10 = json.load(open(os.path.join(ROOT, "llm-qa/outputs/scripts10/scripts10-summary.json"),
                     encoding="utf-8"))
for r in s10:
    print(f"  n=10 {r['model']}: 可运行 {r['runnable_rate']}%")
f20 = glob.glob("/opt/qa/scripts20-*/scripts20-summary.json")
for f in sorted(f20):
    d = json.load(open(f, encoding="utf-8"))[0]
    print(f"  n=20 {d['model']}: 可运行 {d['runnable_rate']}% CI {d['runnable_ci']}")

print("\n===== 4. 性能数据 =====")
for d, expect in (("results-rigor", "static"), ("results-rigor-list", "list")):
    jtls = glob.glob(os.path.join(ROOT, "wp-perf", d, "*.jtl"))
    print(f"  {d}: {len(jtls)} 个 jtl")
    if len(jtls) != 9:
        note(f"{d} 的 jtl 数量不是 9：{len(jtls)}")

print("\n===== 5. 文档中的陈旧数字 =====")
PATTERNS = {
    "旧性能 19.6": r"19\.6\s*TPS",
    "旧保真 36.4": r"36\.4%",
    "旧保真 57.1": r"57\.1%",
    "10 条脚本": r"10\s*条/模型|n=10",
    "12 条缺陷": r"12\s*条缺陷",
    "40 条用例": r"40\s*条用例",
}
for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    if any(k in rel for k in ("node_modules", "outputs")):
        continue
    text = open(f, encoding="utf-8", errors="replace").read()
    for name, pat in PATTERNS.items():
        if re.search(pat, text):
            note(f"{rel}: 仍含「{name}」")

print("\n===== 6. 产物完整性 =====")
NEED = [
    "llm-qa/outputs/scripts20-summary.json",
    "llm-qa/outputs/selector-fidelity10.json",
    "llm-qa/outputs/cost-estimate.json",
    "wp-perf/性能复测结果.md",
    "wp-compat/compat.json",
    "defect-hunt/双版本对照.md",
    "defect-hunt/evidence/status.csv",
    ".github/workflows/ci.yml",
    "llm-qa/评测方法依据.md",
]
for p in NEED:
    full = os.path.join(ROOT, p.replace("/", os.sep))
    if not os.path.exists(full):
        note(f"缺少产物：{p}")

print(f"\n===== 汇总：{len(issues)} 个问题 =====")
for i, s in enumerate(issues, 1):
    print(f"{i:>2}. {s}")
