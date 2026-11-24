#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""大模型测试助手 CLI。

用法：
  python run.py --provider mock --task all
  python run.py --provider deepseek --task all --temperature 0.2
  python run.py --provider ollama --model qwen2.5:3b --task cases
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

from llm_qa import (
    SYS_CASES, SYS_SCRIPTS, SYS_TRIAGE, SYS_REPORT,
    Settings, build_backend, evaluate_cases, evaluate_triage,
    java_syntax_ok, parse_json_array, strip_fences,
    user_cases, user_scripts, user_triage, user_report,
)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")


def load_dotenv(path: str) -> None:
    """极简 .env 加载（不引入额外依赖）"""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_dotenv(os.path.join(BASE, ".env"))


def load(name: str):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        if isinstance(obj, str):
            fh.write(obj)
        else:
            json.dump(obj, fh, ensure_ascii=False, indent=2)


def run_cases(backend, out_dir: str) -> dict:
    features = load("features.json")
    refs = load("reference_titles.json")
    results, rows = {}, []
    for rid, feat in features.items():
        raw = backend.complete(SYS_CASES, user_cases(feat))
        save(os.path.join(out_dir, "cases", f"{rid}.json"), raw)
        m = evaluate_cases(raw, refs)
        m["feature"] = feat["feature"]
        m["id"] = rid
        rows.append(m)
        results[rid] = m
    total = sum(r["count"] for r in rows)
    valid = sum(1 for r in rows if r["valid_json"])
    fields = sum(r["fields_ok"] for r in rows)
    overlap = sum(r["overlap"] for r in rows)
    summary = {
        "features": len(rows),
        "generated_cases": total,
        "valid_json_rate": round(valid / len(rows) * 100, 1),
        "field_complete_rate": round(fields / total * 100, 1) if total else 0,
        "human_overlap_rate": round(overlap / total * 100, 1) if total else 0,
        "new_cases": total - overlap,
    }
    save(os.path.join(out_dir, "cases", "summary.json"), {"summary": summary, "detail": rows})
    return summary


def run_scripts(backend, out_dir: str) -> dict:
    cases = [
        {"id": "TC-AUTH-001", "title": "管理员正确登录", "steps": ["打开登录页", "输入 admin/Admin@2026", "点击登录"], "expected": "进入 wp-admin"},
        {"id": "TC-POST-001", "title": "保存文章草稿", "steps": ["进入新建文章", "填写标题", "点击保存草稿"], "expected": "提示草稿已更新"},
        {"id": "TC-PERM-001", "title": "投稿者无发布按钮", "steps": ["以投稿者登录", "进入新建文章"], "expected": "只有提交复审按钮"},
    ]
    rows = []
    for case in cases:
        raw = backend.complete(SYS_SCRIPTS, user_scripts(case))
        code = strip_fences(raw)
        save(os.path.join(out_dir, "scripts", f"{case['id']}.java"), code)
        ok = java_syntax_ok(code)
        rows.append({"case": case["id"], "syntax_ok": ok, "length": len(code),
                     "has_assert": "assert" in code.lower(), "has_wait": "wait" in code.lower()})
    summary = {
        "cases": len(rows),
        "syntax_ok_rate": round(sum(r["syntax_ok"] for r in rows) / len(rows) * 100, 1),
        "assert_rate": round(sum(r["has_assert"] for r in rows) / len(rows) * 100, 1),
        "wait_rate": round(sum(r["has_wait"] for r in rows) / len(rows) * 100, 1),
    }
    save(os.path.join(out_dir, "scripts", "summary.json"), {"summary": summary, "detail": rows})
    return summary


def run_triage(backend, out_dir: str) -> dict:
    logs = load("failure_logs.json")
    rows = []
    for item in logs:
        raw = backend.complete(SYS_TRIAGE, user_triage(item))
        save(os.path.join(out_dir, "triage", f"{item['id']}.json"), raw)
        m = evaluate_triage(raw, item["gold"])
        m.update({"id": item["id"], "gold": item["gold"], "case": item["case"]})
        rows.append(m)
    summary = {
        "logs": len(rows),
        "accuracy": round(sum(r["match"] for r in rows) / len(rows) * 100, 1),
        "hallucination_to_defect": sum(1 for r in rows if r["gold"] != "系统缺陷" and r["category"] == "系统缺陷"),
    }
    save(os.path.join(out_dir, "triage", "summary.json"), {"summary": summary, "detail": rows})
    return summary


def run_report(backend, out_dir: str) -> dict:
    perf = {
        "scenario": "首页",
        "samples": [{"threads": 10, "tps": 19.6, "avg_ms": 81, "p95_ms": 121},
                    {"threads": 50, "tps": 84.1, "avg_ms": 143, "p95_ms": 263},
                    {"threads": 100, "tps": 91.5, "avg_ms": 519, "p95_ms": 1549},
                    {"threads": 200, "tps": 90.3, "avg_ms": 1457, "p95_ms": 5272}],
        "tuning": "Apache workers 150→300、InnoDB buffer 128M→512M，TPS 91.5→91.6（无效）",
        "cache": "mod_cache 未生效：无缓存头且 Vary: Cookie，缓存目录为空",
    }
    text = backend.complete(SYS_REPORT, user_report(perf))
    save(os.path.join(out_dir, "report", "perf-analysis.md"), text.strip())
    return {"chars": len(text.strip())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="mock", choices=["mock", "dashscope", "deepseek", "ollama"])
    ap.add_argument("--model", default="")
    ap.add_argument("--task", default="all", choices=["cases", "scripts", "triage", "report", "all"])
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    settings = Settings(provider=args.provider, model=args.model, temperature=args.temperature,
                        max_tokens=args.max_tokens).resolve()
    backend = build_backend(settings)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = args.out or os.path.join(BASE, "outputs", f"{args.provider}-{stamp}")

    print(f"provider={settings.provider} model={settings.model} out={out_dir}")
    report = {"provider": settings.provider, "model": settings.model,
              "temperature": settings.temperature, "time": stamp}

    if args.task in ("cases", "all"):
        report["cases"] = run_cases(backend, out_dir)
        print("  用例生成:", report["cases"])
    if args.task in ("scripts", "all"):
        report["scripts"] = run_scripts(backend, out_dir)
        print("  脚本生成:", report["scripts"])
    if args.task in ("triage", "all"):
        report["triage"] = run_triage(backend, out_dir)
        print("  日志归因:", report["triage"])
    if args.task in ("report", "all"):
        report["report"] = run_report(backend, out_dir)
        print("  报告生成:", report["report"])

    save(os.path.join(out_dir, "metrics.json"), report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
