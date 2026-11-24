#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从已保存的用例 JSON 反算严格合规率与需求覆盖率（无需重新调用模型）。"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluate_v2 import coverage_of, strict_case_check

BASE = os.path.dirname(os.path.abspath(__file__))
POINTS = json.load(open(os.path.join(BASE, "data", "coverage_points20.json"), encoding="utf-8"))


def load(path):
    raw = open(path, encoding="utf-8").read()
    for fn in (lambda s: json.loads(s),
               lambda s: json.loads(s, strict=False),
               lambda s: json.loads(__import__("re").search(r"\[.*\]", s, __import__("re").S).group(0),
                                    strict=False)):
        try:
            return fn(raw)
        except Exception:
            continue
    return None


def score(dirpath: str) -> dict:
    strict_ok = strict_total = cov_hit = cov_total = 0
    bad = []
    for f in sorted(glob.glob(os.path.join(dirpath, "*.json"))):
        fid = os.path.basename(f).replace(".json", "")
        data = load(f)
        chk = strict_case_check(data)
        cov = coverage_of(data if isinstance(data, list) else [],
                          POINTS.get(fid, {}).get("must_cover", []))
        strict_ok += chk["strict_ok"]
        strict_total += chk["count"]
        cov_hit += cov["covered"]
        cov_total += cov["total"]
        if chk["count"] and chk["strict_ok"] / chk["count"] < 1:
            bad.append((fid, chk["strict_ok"], chk["count"]))
    return {
        "cases": strict_total,
        "strict_ok": strict_ok,
        "strict_rate": round(strict_ok / strict_total * 100, 1) if strict_total else 0,
        "coverage": round(cov_hit / cov_total * 100, 1) if cov_total else 0,
        "imperfect_features": bad,
    }


for name, d in (("DeepSeek-V4-Pro", "/opt/qa/rigor-pro/cases/rep1"),
                ("Qwen-Plus", "/opt/qa/rigor-qwen/cases/rep1")):
    if not os.path.isdir(d):
        print(name, "目录不存在:", d)
        continue
    r = score(d)
    print(f"{name:<22} 用例 {r['cases']:>4}  严格合规 {r['strict_rate']:>5.1f}%  覆盖 {r['coverage']:>5.1f}%")
    if r["imperfect_features"]:
        print("   非满分的功能点:", r["imperfect_features"][:6])
    json.dump(r, open(os.path.join(BASE, "outputs", f"score-{name}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
