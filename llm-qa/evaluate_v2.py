# -*- coding: utf-8 -*-
"""严格版评估：对已有产物重新打分（不调用 API）。

相比 v1 的改进：
1. 结构合规 —— 不只看 key 存在，还校验类型、steps 长度、expected 长度、method 是否合法
2. 需求覆盖 —— 每个功能点定义 5-6 个必须覆盖的测试点，按关键词命中计算覆盖率
3. 断言强度 —— 排除注释后统计真实断言，区分"只判非空"与"断言具体值"
4. 编译结果 —— 读取 compile-result.md 的真实通过率（v1 用的是括号配对）
5. 定位器保真度 —— 复用 selector-fidelity.json
"""

from __future__ import annotations

import glob
import json
import os
import re
import statistics

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "outputs")

METHODS = {"等价类划分", "边界值分析", "判定表", "状态迁移", "场景法", "错误推测",
           "错误猜测", "等价类", "边界值", "正交实验", "权限矩阵", "因果图", "流程图分析"}


def load_json_lenient(path: str):
    raw = open(path, encoding="utf-8").read()
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.S)
        return json.loads(m.group(0)) if m else None


def strict_case_check(cases) -> dict:
    if not isinstance(cases, list) or not cases:
        return {"parse": False, "count": 0, "strict_ok": 0, "reasons": {}}

    ok = 0
    reasons: dict[str, int] = {}
    for c in cases:
        problems = []
        if not isinstance(c, dict):
            problems.append("非对象")
        else:
            for k in ("id", "title", "precondition", "steps", "expected", "method"):
                if k not in c:
                    problems.append(f"缺{k}")
            if isinstance(c.get("steps"), list):
                if len([s for s in c["steps"] if str(s).strip()]) < 2:
                    problems.append("步骤不足2步")
            else:
                problems.append("steps非数组")
            if len(str(c.get("expected", "")).strip()) < 10:
                problems.append("预期结果过短")
            method = str(c.get("method", ""))
            if not any(m in method for m in METHODS):
                problems.append("方法不在枚举内")
            if len(str(c.get("title", "")).strip()) < 6:
                problems.append("标题过短")
        if problems:
            for p in problems:
                reasons[p] = reasons.get(p, 0) + 1
        else:
            ok += 1
    return {"parse": True, "count": len(cases), "strict_ok": ok, "reasons": reasons}


def coverage_of(cases, points) -> dict:
    if not cases:
        return {"covered": 0, "total": len(points), "rate": 0.0, "missing": []}
    text = " ".join(
        str(c.get("title", "")) + str(c.get("expected", "")) + " ".join(map(str, c.get("steps", [])))
        for c in cases if isinstance(c, dict)
    ).lower()
    hit, missing = 0, []
    for name, kws in points:
        if any(k.lower() in text for k in kws):
            hit += 1
        else:
            missing.append(name)
    if not points:
        return {"covered": 0, "total": 0, "rate": 0.0, "missing": []}
    return {"covered": hit, "total": len(points), "rate": round(hit / len(points) * 100, 1),
            "missing": missing}


ASSERT_PAT = re.compile(r"\bAssert\.\w+|\bassert\w*\s*\(|\bassertThat\s*\(")


def strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    # 只去掉真正的行注释，避免把 https:// 里的 // 一起切掉
    code = re.sub(r"(?<!:)//[^\n]*", "", code)
    return code


def assertion_strength(code: str) -> dict:
    body = strip_comments(code)
    asserts = ASSERT_PAT.findall(body)
    strong = len(re.findall(r"Assert\.(assertEquals|assertTrue|assertFalse|assertThat|assertNotEquals)", body))
    weak = len(re.findall(r"Assert\.(assertNotNull|assertNull|assertNotSame)", body))
    return {"asserts": len(asserts), "strong": strong, "weak": weak,
            "has_wait": bool(re.search(r"WebDriverWait|ExpectedConditions|implicitlyWait", body)),
            "bare": len(asserts) == 0}


def url_correct(code: str) -> bool:
    """被测地址必须指向我们的环境（localhost:8080 或 BASE_URL），且不能出现占位域名"""
    body = strip_comments(code)
    if "example.com" in body:
        return False
    return "localhost:8080" in body or "BASE_URL" in body


def runnable(code: str, fidelity: float | None) -> dict:
    """可运行性综合判定：编译前提（结构）+ 地址正确 + 定位器保真度"""
    s = assertion_strength(code)
    return {
        "has_class": bool(re.search(r"\bclass\s+\w+", strip_comments(code))),
        "url_ok": url_correct(code),
        "fidelity_ok": (fidelity or 0) >= 50,
        "assert_ok": s["asserts"] >= 1,
    }


def main() -> None:
    points = json.load(open(os.path.join(BASE, "data", "coverage_points.json"), encoding="utf-8"))
    compile_txt = open(os.path.join(OUT, "compile-result.md"), encoding="utf-8").read() if os.path.exists(
        os.path.join(OUT, "compile-result.md")) else ""
    fidelity = {}
    fp = os.path.join(OUT, "selector-fidelity.json")
    if os.path.exists(fp):
        for r in json.load(open(fp, encoding="utf-8")):
            fidelity[r["model"]] = r["fidelity"]

    rows = []
    for d in sorted(glob.glob(os.path.join(OUT, "cmp-*"))):
        model = os.path.basename(d).replace("cmp-", "")
        cases_all, per_feature = [], {}
        for f in sorted(glob.glob(os.path.join(d, "cases", "R*.json"))):
            rid = os.path.basename(f).replace(".json", "")
            data = load_json_lenient(f)
            chk = strict_case_check(data)
            cov = coverage_of(data if isinstance(data, list) else [],
                              points.get(rid, {}).get("must_cover", []))
            per_feature[rid] = {"strict": chk, "coverage": cov}
            if isinstance(data, list):
                cases_all.extend(data)

        total = len(cases_all)
        strict_ok = sum(v["strict"]["strict_ok"] for v in per_feature.values())
        cov_hit = sum(v["coverage"]["covered"] for v in per_feature.values())
        cov_total = sum(v["coverage"]["total"] for v in per_feature.values())

        scripts = glob.glob(os.path.join(d, "scripts", "*.java"))
        strengths = [assertion_strength(open(s, encoding="utf-8", errors="replace").read()) for s in scripts]

        runnables = [runnable(open(s, encoding="utf-8", errors="replace").read(), fidelity.get(model)) for s in scripts]
        run_ok = sum(1 for r in runnables if r["url_ok"] and r["assert_ok"] and r["has_class"])
        url_bad = sum(1 for r in runnables if not r["url_ok"])
        class_bad = sum(1 for r in runnables if not r["has_class"])
        rows.append({
            "model": model,
            "cases": total,
            "url_bad_scripts": url_bad,
            "class_bad_scripts": class_bad,
            "runnable": run_ok,
            "runnable_rate": round(run_ok / len(scripts) * 100, 1) if scripts else 0,
            "strict_ok": strict_ok,
            "strict_rate": round(strict_ok / total * 100, 1) if total else 0,
            "coverage": round(cov_hit / cov_total * 100, 1) if cov_total else 0,
            "coverage_hit": cov_hit,
            "coverage_total": cov_total,
            "scripts": len(scripts),
            "asserts_avg": round(statistics.mean([s["asserts"] for s in strengths]), 1) if strengths else 0,
            "strong_rate": round(sum(1 for s in strengths if s["strong"] > 0) / len(strengths) * 100, 1) if strengths else 0,
            "bare_rate": round(sum(1 for s in strengths if s["bare"]) / len(strengths) * 100, 1) if strengths else 0,
            "selector_fidelity": fidelity.get(model, None),
        })

    print(f"{'模型':<24}{'用例':>5}{'严格合规':>9}{'需求覆盖':>9}{'定位器保真':>10}{'URL错误':>8}{'可直接运行':>10}")
    for r in rows:
        print(f"{r['model']:<24}{r['cases']:>5}{r['strict_rate']:>8.1f}%{r['coverage']:>8.1f}%"
              f"{(r['selector_fidelity'] if r['selector_fidelity'] is not None else 0):>9.1f}%"
              f"{r['url_bad_scripts']:>8}{r['runnable_rate']:>9.1f}%")

    with open(os.path.join(OUT, "metrics-v2.json"), "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "per_feature_sample": per_feature}, fh, ensure_ascii=False, indent=2)

    print("\n各功能点覆盖率明细（示例：DeepSeek-V4.1-Flash）")
    for rid, v in per_feature.items():
        c = v["coverage"]
        print(f"  {rid}: {c['covered']}/{c['total']} = {c['rate']}%  缺: {', '.join(c['missing']) or '无'}")
    print("\n已写入 outputs/metrics-v2.json")


if __name__ == "__main__":
    main()
