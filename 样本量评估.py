# -*- coding: utf-8 -*-
"""计算关键比例的 Wilson 95% 置信区间，评估样本量是否足够。"""

from __future__ import annotations

import json
import math
import os

ROOT = r"E:\软件质量保证与测试课程设计"


def wilson(k: int, n: int, z: float = 1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, (c - h) * 100), min(100, (c + h) * 100)


ITEMS = [
    ("用例通过率", 39, 43, "43 条全部执行"),
    ("结构可运行率（Flash）", 13, 20, "20 条脚本"),
    ("严格可运行率（Flash）", 1, 20, "20 条脚本"),
    ("严格可运行率（Pro）", 0, 20, "20 条脚本"),
    ("严格可运行率（Qwen）", 0, 20, "20 条脚本"),
    ("归因准确率（Flash）", 23, 24, "24 条平衡样本"),
    ("归因准确率（Pro）", 22, 24, "24 条平衡样本"),
    ("权限矩阵符合率", 30, 30, "30 格 × 3 次"),
    ("兼容性通过率", 12, 12, "12 组"),
    ("双版本探针命中率", 11, 12, "12 项探针"),
]

lines = []
print(f"{'指标':<26}{'k/n':>9}{'点估计':>9}{'Wilson 95% CI':>20}{'CI 宽度':>9}")
print("-" * 78)
for name, k, n, note in ITEMS:
    lo, hi = wilson(k, n)
    width = hi - lo
    print(f"{name:<26}{f'{k}/{n}':>9}{k/n*100:>8.1f}%{f'[{lo:.1f}%, {hi:.1f}%]':>20}{width:>8.1f}%")
    lines.append({"指标": name, "k": k, "n": n, "点估计": round(k / n * 100, 1),
                  "CI下限": round(lo, 1), "CI上限": round(hi, 1),
                  "CI宽度": round(width, 1), "说明": note})

print("\n判读标准：CI 宽度 <10% 说明样本充足；10%–25% 为可接受；>25% 说明样本偏少，结论需谨慎。")
json.dump(lines, open(os.path.join(ROOT, "样本量评估.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
