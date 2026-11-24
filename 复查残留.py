# -*- coding: utf-8 -*-
"""最终一致性复查：区分"历史引用"与"陈旧残留"。"""

from __future__ import annotations

import glob
import io
import os
import re

ROOT = r"E:\软件质量保证与测试课程设计"

# 允许出现旧数字的上下文关键词（历史/演进/作废说明）
HISTORY_HINTS = ("阶段", "第一次", "第二次", "第三次", "早期", "历史", "作废", "已废弃",
                 "旧数据", "旧方法", "v1", "演进", "回落")

CHECKS = {
    "旧保真 36.4/57.1": r"36\.4%|57\.1%",
    "旧性能 19.6": r"19\.6\s*TPS",
    "10 条脚本": r"n=10|10\s*条/模型",
}

problems = []
for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    if "outputs" in rel or "_archive" in rel:
        continue
    for lineno, line in enumerate(io.open(f, encoding="utf-8", errors="replace"), 1):
        for name, pat in CHECKS.items():
            if re.search(pat, line):
                if any(h in line for h in HISTORY_HINTS):
                    continue
                problems.append(f"{rel}:{lineno} [{name}] {line.strip()[:80]}")

print(f"可疑残留：{len(problems)} 处")
for p in problems:
    print(" ", p)
