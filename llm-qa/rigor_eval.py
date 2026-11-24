#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""严谨版评测：20 功能点 × 3 次重复 + 10 个脚本样本 + 24 条归因样本。

输出均值、标准差与 95% 置信区间（t 分布，df = n-1）。
"""

from __future__ import annotations

import json
import math
import os
import re
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_qa import (SYS_CASES, SYS_SCRIPTS, SYS_TRIAGE, Settings, build_backend,
                    evaluate_triage, java_syntax_ok, strip_fences,
                    user_cases, user_scripts, user_triage)
from evaluate_v2 import (assertion_strength, coverage_of, strict_case_check,
                         url_correct)

BASE = os.path.dirname(os.path.abspath(__file__))
FEATURES = json.load(open(os.path.join(BASE, "data", "features20.json"), encoding="utf-8"))
POINTS = json.load(open(os.path.join(BASE, "data", "coverage_points20.json"), encoding="utf-8"))
TRIAGE = json.load(open(os.path.join(BASE, "data", "triage24.json"), encoding="utf-8"))
OUT = os.environ.get("RIGOR_OUT", "/opt/qa/rigor-out")
os.makedirs(OUT, exist_ok=True)

MODELS = [("deepseek-v4.1-flash", "DeepSeek-V4.1-Flash"),
          ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
          ("qwen-plus", "Qwen-Plus")]

REPS = 3
SCRIPT_CASES = [
    {"id": "TC-AUTH-001", "title": "管理员正确登录", "steps": ["打开登录页", "输入 admin/Admin@2026", "点击登录"], "expected": "进入 wp-admin"},
    {"id": "TC-AUTH-002", "title": "错误密码登录失败", "steps": ["打开登录页", "输入正确用户名与错误密码", "提交"], "expected": "提示密码不正确"},
    {"id": "TC-POST-001", "title": "保存文章草稿", "steps": ["进入新建文章", "填写标题", "点击保存草稿"], "expected": "提示草稿已更新"},
    {"id": "TC-POST-002", "title": "草稿发布", "steps": ["打开草稿", "点击发布"], "expected": "状态变为已发布"},
    {"id": "TC-MEDIA-001", "title": "上传图片", "steps": ["进入媒体库", "选择图片", "上传"], "expected": "上传成功并生成缩略图"},
    {"id": "TC-COMM-001", "title": "提交评论进入待审", "steps": ["打开文章", "填写评论", "提交"], "expected": "提示等待审核"},
    {"id": "TC-API-001", "title": "匿名读取文章列表", "steps": ["GET /wp-json/wp/v2/posts"], "expected": "仅返回已发布文章"},
    {"id": "TC-PERM-001", "title": "投稿者无发布按钮", "steps": ["以投稿者登录", "进入新建文章页"], "expected": "只有提交复审按钮"},
    {"id": "TC-PERM-002", "title": "订阅者不能进后台", "steps": ["以订阅者登录", "访问 /wp-admin/edit.php"], "expected": "被拒绝"},
    {"id": "TC-SET-001", "title": "修改站点标题", "steps": ["进入设置-常规", "修改标题", "保存"], "expected": "前台标题同步更新"},
    {"id": "TC-AUTH-005", "title": "连续错误密码无锁定", "steps": ["连续 5 次错误密码登录"], "expected": "出现验证码或锁定提示"},
    {"id": "TC-POST-003", "title": "定时发布文章", "steps": ["新建文章", "设置未来时间", "保存"], "expected": "状态为已安排"},
    {"id": "TC-POST-006", "title": "文章移入回收站并还原", "steps": ["打开文章列表", "移入回收站", "从回收站还原"], "expected": "文章恢复为已发布"},
    {"id": "TC-MEDIA-002", "title": "上传超限文件", "steps": ["进入媒体库", "选择 20MB 图片", "上传"], "expected": "提示文件超过大小限制"},
    {"id": "TC-COMM-004", "title": "管理员回复评论", "steps": ["打开后台评论列表", "对某条评论回复", "提交"], "expected": "前台显示嵌套回复"},
    {"id": "TC-API-004", "title": "REST 分页边界", "steps": ["请求 per_page=101"], "expected": "返回 400 参数错误"},
    {"id": "TC-PERM-004", "title": "编辑尝试新建用户", "steps": ["以编辑身份登录", "访问新建用户页"], "expected": "被拒绝访问"},
    {"id": "TC-PERM-005", "title": "作者删除他人文章", "steps": ["以作者身份登录", "尝试删除他人文章"], "expected": "无删除入口或操作被拒"},
    {"id": "TC-SET-002", "title": "修改固定链接结构", "steps": ["进入设置-固定链接", "选择文章名结构", "保存"], "expected": "旧链接 301 跳转到新链接"},
    {"id": "TC-POST-007", "title": "后台搜索文章", "steps": ["进入文章列表", "搜索关键词", "回车"], "expected": "结果只包含匹配文章"},
]

ENV = os.path.join(BASE, ".env")
if os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

T975 = {1: 12.706, 2: 4.303, 3: 3.182}


def ci95(values: list[float]) -> tuple[float, float, float]:
    n = len(values)
    mean = statistics.mean(values)
    if n < 2:
        return mean, 0.0, 0.0
    sd = statistics.stdev(values)
    half = T975.get(n - 1, 1.96) * sd / math.sqrt(n)
    return mean, sd, half


def run_cases(backend, rep: int) -> dict:
    strict_ok = strict_total = cov_hit = cov_total = 0
    total_cases = 0
    for fid, feat in FEATURES.items():
        raw = backend.complete(SYS_CASES, user_cases(feat))
        path = os.path.join(OUT, "cases", f"rep{rep}", f"{fid}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(raw)
        data = None
        for loader in (lambda s: json.loads(s),
                       lambda s: json.loads(s, strict=False),
                       lambda s: json.loads(re.search(r"\[.*\]", s, re.S).group(0), strict=False)):
            try:
                data = loader(strip_fences(raw))
                break
            except Exception:
                continue
        chk = strict_case_check(data)
        cov = coverage_of(data if isinstance(data, list) else [], POINTS.get(fid, {}).get("must_cover", []))
        strict_ok += chk["strict_ok"]
        strict_total += chk["count"]
        total_cases += chk["count"]
        cov_hit += cov["covered"]
        cov_total += cov["total"]
    return {"cases": total_cases,
            "strict_rate": strict_ok / strict_total * 100 if strict_total else 0,
            "coverage": cov_hit / cov_total * 100 if cov_total else 0}


def run_scripts(backend) -> dict:
    rows = []
    for case in SCRIPT_CASES:
        code = strip_fences(backend.complete(SYS_SCRIPTS, user_scripts(case)))
        p = os.path.join(OUT, "scripts", f"{case['id']}.java")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(code)
        s = assertion_strength(code)
        rows.append({
            "has_class": bool(__import__("re").search(r"\bclass\s+\w+", code)),
            "url_ok": url_correct(code),
            "asserts": s["asserts"],
            "bare": s["bare"],
        })
    n = len(rows)
    return {
        "scripts": n,
        "class_rate": sum(r["has_class"] for r in rows) / n * 100,
        "url_ok_rate": sum(r["url_ok"] for r in rows) / n * 100,
        "assert_rate": sum(1 for r in rows if r["asserts"] > 0) / n * 100,
        "runnable_rate": sum(1 for r in rows if r["has_class"] and r["url_ok"] and r["asserts"] > 0) / n * 100,
    }


def run_triage(backend) -> dict:
    ok = 0
    wrong_defect = 0
    per = []
    for item in TRIAGE:
        raw = backend.complete(SYS_TRIAGE, user_triage(item))
        m = evaluate_triage(raw, item["gold"])
        ok += m["match"]
        if item["gold"] != "系统缺陷" and m["category"] == "系统缺陷":
            wrong_defect += 1
        per.append({"id": item["id"], "gold": item["gold"], "got": m["category"], "match": m["match"]})
    return {"n": len(TRIAGE), "accuracy": ok / len(TRIAGE) * 100,
            "wrong_defect": wrong_defect, "detail": per}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="")
    ap.add_argument("--out", default="summary.json")
    args = ap.parse_args()
    targets = [m for m in MODELS if not args.model or m[0] == args.model]
    summary = []
    for model, label in targets:
        s = Settings(provider="dashscope", model=model, max_tokens=8000).resolve()
        backend = build_backend(s)
        print(f"\n########## {label} ##########", flush=True)

        reps = []
        for r in range(1, REPS + 1):
            t0 = time.time()
            m = run_cases(backend, r)
            m["rep"] = r
            reps.append(m)
            print(f"  rep{r}: 用例 {m['cases']} 条，严格合规 {m['strict_rate']:.1f}%，"
                  f"覆盖 {m['coverage']:.1f}%（{time.time()-t0:.0f}s）", flush=True)

        strict_vals = [x["strict_rate"] for x in reps]
        cov_vals = [x["coverage"] for x in reps]
        mean_s, sd_s, ci_s = ci95(strict_vals)
        mean_c, sd_c, ci_c = ci95(cov_vals)

        sc = run_scripts(backend)
        tri = run_triage(backend)

        row = {
            "model": label,
            "cases_per_rep": reps[0]["cases"],
            "strict_mean": round(mean_s, 1), "strict_sd": round(sd_s, 1), "strict_ci": round(ci_s, 1),
            "coverage_mean": round(mean_c, 1), "coverage_sd": round(sd_c, 1), "coverage_ci": round(ci_c, 1),
            **{k: round(v, 1) if isinstance(v, float) else v for k, v in sc.items()},
            "triage_n": tri["n"], "triage_acc": round(tri["accuracy"], 1),
            "triage_wrong_defect": tri["wrong_defect"],
            "reps": reps, "triage_detail": tri["detail"],
        }
        summary.append(row)
        json.dump(summary, open(os.path.join(OUT, args.out), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"  -> 严格合规 {mean_s:.1f}±{ci_s:.1f}%，覆盖 {mean_c:.1f}±{ci_c:.1f}%，"
              f"可运行 {sc['runnable_rate']:.0f}%，归因 {tri['accuracy']:.1f}%", flush=True)

    print("\n================ 严谨版汇总 ================")
    hdr = f"{'模型':<22}{'用例/次':>7}{'严格合规(均值±CI)':>20}{'需求覆盖(均值±CI)':>20}{'可运行':>7}{'归因':>7}"
    print(hdr)
    for r in summary:
        print(f"{r['model']:<22}{r['cases_per_rep']:>7}"
              f"{r['strict_mean']:>12.1f}±{r['strict_ci']:<6.1f}"
              f"{r['coverage_mean']:>13.1f}±{r['coverage_ci']:<6.1f}"
              f"{r['runnable_rate']:>6.0f}%{r['triage_acc']:>6.1f}%")


if __name__ == "__main__":
    main()
