#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 WPScan 经典检查项补充探测（版本暴露、用户枚举、信息文件）。"""

from __future__ import annotations

import re

import requests

BASE = "http://localhost:8080"
S = requests.Session()
S.headers.update({"User-Agent": "qa-wpscan-lite/1.0"})
FINDINGS = []


def rec(cid, title, expect, actual, status, evidence=""):
    FINDINGS.append({"id": cid, "title": title, "expect": expect, "actual": actual,
                     "status": status, "evidence": evidence[:300]})
    print(f"[{status:<7}] {cid} {title} -> {actual}  | {evidence[:70]}")


def get(path, **kw):
    return S.get(BASE + path, timeout=20, allow_redirects=False, **kw)


# 1. readme.html 版本暴露
r = get("/readme.html")
ver = ""
if r.status_code == 200:
    m = re.search(r"Version\s*([0-9.]+)", r.text)
    ver = m.group(1) if m else "未解析到版本"
rec("WPS-01", "readme.html 可访问（暴露版本）", "403/404",
    f"HTTP {r.status_code}，版本={ver or '—'}", "DEFECT" if r.status_code == 200 else "PASS",
    r.text[:150])

# 2. license.txt
r = get("/license.txt")
rec("WPS-02", "license.txt 可访问", "影响很小，仅记录",
    f"HTTP {r.status_code}", "OBSERVE" if r.status_code == 200 else "PASS", "")

# 3. robots.txt
r = get("/robots.txt")
body = r.text[:300].replace("\n", " ")
rec("WPS-03", "robots.txt", "存在且不暴露敏感路径",
    f"HTTP {r.status_code} 内容={body[:80]}", "PASS" if r.status_code == 200 else "OBSERVE", body)

# 4. 用户枚举（?author=N）
enum = []
for uid in (1, 2):
    r = get(f"/?author={uid}")
    loc = r.headers.get("Location", "")
    enum.append(f"author={uid} -> {r.status_code} {loc}")
reveal = any("author/" in e for e in enum)
rec("WPS-04", "通过 ?author=N 枚举用户名", "不重定向到作者归档页",
    "；".join(enum)[:160], "DEFECT" if reveal else "PASS", "")

# 5. wp-json 索引是否暴露版本/命名空间
r = get("/wp-json/")
ns = []
if r.status_code == 200:
    try:
        ns = r.json().get("namespaces", [])
    except Exception:  # noqa: BLE001
        pass
rec("WPS-05", "/wp-json/ 索引暴露命名空间", "允许（正常特性），仅记录",
    f"HTTP {r.status_code}，命名空间 {len(ns)} 个", "OBSERVE" if ns else "PASS", str(ns)[:120])

# 6. 版本文件
for path in ("/wp-includes/version.php", "/wp-config-sample.php"):
    r = get(path)
    rec(f"WPS-06{ 'a' if 'version' in path else 'b' }", f"{path} 直接访问", "空白或 403/404",
        f"HTTP {r.status_code}，{len(r.content)} 字节",
        "DEFECT" if r.status_code == 200 and len(r.content) > 100 else "PASS", r.text[:100])

# 7. 数据库错误回显（构造非法参数）
r = get("/wp-json/wp/v2/posts?orderby=DROP")
rec("WPS-07", "REST 非法参数是否回显内部错误", "仅返回参数错误，不暴露 SQL",
    f"HTTP {r.status_code}", "PASS" if r.status_code < 500 else "DEFECT", r.text[:150])

# 8. 上传目录列表（上一轮已发现，复核）
r = get("/wp-content/uploads/")
rec("WPS-08", "上传目录列表（复核）", "403/404",
    f"HTTP {r.status_code}", "DEFECT" if r.status_code == 200 and "Index of" in r.text else "PASS", "")

df = [f for f in FINDINGS if f["status"] == "DEFECT"]
ob = [f for f in FINDINGS if f["status"] == "OBSERVE"]
print(f"\n补充探测 {len(FINDINGS)} 项：DEFECT {len(df)}，OBSERVE {len(ob)}")
import json
import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings3.json"), "w", encoding="utf-8") as fh:
    json.dump(FINDINGS, fh, ensure_ascii=False, indent=2)
