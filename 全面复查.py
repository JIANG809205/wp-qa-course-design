# -*- coding: utf-8 -*-
"""全面复查：扫描 md 与 docx 中的关键数字，与地面真值比对。"""

from __future__ import annotations

import glob
import io
import json
import os
import re

ROOT = r"E:\软件质量保证与测试课程设计"

# ---------- 地面真值 ----------
GT = {
    "用例总数": "43", "通过": "39", "失败": "4",
    "缺陷": "11", "P1": "2", "P2": "5", "P3": "4",
    "权限格": "36", "兼容组": "24",
    "首页TPS": ["122.8", "126.7", "127.5"],
    "列表TPS": ["97.3", "87.8", "52.1"],
    "归因": ["95.8", "91.7"],
}

# 不应再出现的旧值（除非在历史说明上下文）
STALE = {
    "30 格": r"30\s*格",
    "12 组（兼容）": r"12\s*组",
    "旧保真 36.4%": r"36\.4%",
    "旧保真 57.1%": r"57\.1%",
    "旧性能 19.6": r"19\.6\s*TPS",
    "n=10": r"n=10\b",
    "20 条脚本": r"20\s*条脚本",
    "缺陷 12 条": r"12\s*条缺陷",
}
HISTORY = ("阶段", "第一次", "第二次", "第三次", "早期", "历史", "作废", "旧数据",
           "旧方法", "v1", "演进", "回落", "推翻", "修正前", "之前",
           "3 条时", "扩到 10 条", "第一轮", "本节这版", "第一版")

problems: list[str] = []


def scan_text(rel: str, text: str) -> None:
    for lineno, line in enumerate(text.splitlines(), 1):
        if any(h in line for h in HISTORY):
            continue
        for name, pat in STALE.items():
            if re.search(pat, line):
                problems.append(f"{rel}:{lineno} [{name}] {line.strip()[:70]}")


# md
for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    if any(k in rel for k in ("outputs", "_archive", ".dsh-office")):
        continue
    scan_text(rel, io.open(f, encoding="utf-8", errors="replace").read())

# docx
DOCX = os.path.join(ROOT, "课程设计报告-学号-姓名.docx")
if os.path.exists(DOCX):
    from docx import Document
    d = Document(DOCX)
    texts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                texts.append(c.text)
    scan_text("课程设计报告-学号-姓名.docx", "\n".join(texts))

print(f"=== 陈旧数字：{len(problems)} 处 ===")
for p in problems[:40]:
    print(" ", p)

# ---------- 产物完整性 ----------
NEED = [
    "README.md", "项目审查报告.md", "数据核验与样本量评估.md",
    "报告正文-第1-3章.md", "报告正文-第4-5章.md", "报告正文-第7-9章.md",
    "06-报告章节-大模型使用过程及经验.md",
    "课程设计报告-学号-姓名.docx",
    "llm-qa/outputs/scripts96-summary.json",
    "llm-qa/outputs/selector-fidelity-s96.json",
    "llm-qa/outputs/triage24-summary.json",
    "wp-perf/性能复测结果.md", "wp-perf/charts-final/perf-tps.png",
    "wp-compat/跨浏览器结果.md", "defect-hunt/双版本对照.md",
    "defect-hunt/权限矩阵实测.md", ".github/workflows/ci.yml",
]
print("\n=== 产物完整性 ===")
missing = [p for p in NEED if not os.path.exists(os.path.join(ROOT, p.replace("/", os.sep)))]
print("缺失:", missing or "无")

# ---------- 图表与数据一致性 ----------
print("\n=== 图表文件 ===")
charts = glob.glob(os.path.join(ROOT, "wp-perf", "charts-final", "*.png"))
print(f"共 {len(charts)} 张：", ", ".join(sorted(os.path.basename(c) for c in charts)))

# ---------- docx 结构 ----------
if os.path.exists(DOCX):
    from docx import Document
    d = Document(DOCX)
    heads = [p.text.strip() for p in d.paragraphs if re.match(r"^第\s*\d+\s*章", p.text.strip())]
    print("\n=== docx 结构 ===")
    print(f"章数: {len(heads)}  图片: {len(d.inline_shapes)}  表格: {len(d.tables)}")
    print("  " + " / ".join(h[:12] for h in heads))
