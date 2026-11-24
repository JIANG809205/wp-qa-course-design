#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""双版本对照：对 7.1.4 与 7.1.5 跑同一套 12 项探针，统计检出差异。"""

from __future__ import annotations

import json
import os
import re
import sys

import requests

BASES = {"7.1.5": os.getenv("BASE_NEW", "http://localhost:8080"),
         "7.1.4": os.getenv("BASE_OLD", "http://localhost:8082")}

PWD = "Admin@2026"


def get(base, path, **kw):
    return requests.get(base + path, timeout=20, allow_redirects=False, **kw)


def login(base, user="admin", pwd=PWD):
    s = requests.Session()
    s.get(f"{base}/wp-login.php", timeout=20)
    s.post(f"{base}/wp-login.php",
           data={"log": user, "pwd": pwd, "wp-submit": "登录", "testcookie": "1"},
           timeout=20, allow_redirects=True)
    return s


def nonce(s, base):
    r = s.get(f"{base}/wp-admin/admin-ajax.php?action=rest-nonce", timeout=20)
    return r.text.strip() if r.status_code == 200 else ""


def probes(base: str) -> dict:
    out = {}

    # P01 安全响应头
    h = get(base, "/").headers
    need = ["X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"]
    out["P01 安全响应头"] = any(k.lower() in {x.lower() for x in h} for k in need) is False

    # P02 debug.log 可下载
    r = get(base, "/wp-content/debug.log")
    out["P02 debug.log 可下载"] = r.status_code == 200 and len(r.content) > 0

    # P03 上传目录列表
    r = get(base, "/wp-content/uploads/")
    out["P03 上传目录列表"] = r.status_code == 200 and "Index of" in r.text

    # P04 readme.html
    out["P04 readme.html 可访问"] = get(base, "/readme.html").status_code == 200

    # P05 xmlrpc 开放
    r = requests.post(f"{base}/xmlrpc.php",
                      data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>',
                      timeout=20)
    out["P05 XML-RPC 开放"] = r.status_code == 200 and "methodResponse" in r.text

    # P06 作者枚举
    r = get(base, "/?author=1")
    out["P06 作者枚举"] = r.status_code in (301, 302) and "/author/" in r.headers.get("Location", "")

    # P07 REST 用户列表匿名可读
    r = get(base, "/wp-json/wp/v2/users")
    out["P07 REST 用户匿名可读"] = r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0

    # P08 空文件上传返回 500
    s = login(base)
    n = nonce(s, base)
    r = s.post(f"{base}/wp-json/wp/v2/media", headers={"X-WP-Nonce": n},
               files={"file": ("empty.png", b"", "image/png")}, timeout=30)
    out["P08 空文件上传 500"] = r.status_code >= 500

    # P09 重复用户名返回 500
    r = s.post(f"{base}/wp-json/wp/v2/users", headers={"X-WP-Nonce": n},
               json={"username": "admin", "email": "dup@example.com",
                     "password": "Dup@2026", "roles": ["subscriber"]}, timeout=30)
    out["P09 重名用户返回 500"] = r.status_code >= 500

    # P10 登录无次数限制
    codes = []
    for _ in range(3):
        rr = requests.post(f"{base}/wp-login.php",
                           data={"log": "admin", "pwd": "wrong-pass", "wp-submit": "登录",
                                 "testcookie": "1"}, timeout=20, allow_redirects=False)
        codes.append(rr.status_code)
    out["P10 登录无失败限制"] = all(c in (200, 302) for c in codes)

    # P11 REST 非法参数是否 400
    r = get(base, "/wp-json/wp/v2/posts?status=bogus")
    out["P11 非法参数 500"] = r.status_code >= 500

    # P12 license.txt / 版本指纹
    r = get(base, "/license.txt")
    out["P12 license.txt 可访问"] = r.status_code == 200

    return out


if __name__ == "__main__":
    results = {}
    for ver, base in BASES.items():
        try:
            code = get(base, "/").status_code
        except Exception as e:  # noqa: BLE001
            print(f"{ver}: 不可达 {e}")
            continue
        print(f"\n===== {ver} ({base}) HTTP {code} =====")
        try:
            results[ver] = probes(base)
        except Exception as e:  # noqa: BLE001
            print(f"  探针异常: {e}")
            results[ver] = {}

    if len(results) == 2:
        keys = sorted(set(results["7.1.5"]) | set(results["7.1.4"]))
        print(f"\n{'探针':<24}{'7.1.5':>8}{'7.1.4':>8}")
        both = only_new = only_old = 0
        for k in keys:
            a = "命中" if results["7.1.5"].get(k) else "—"
            b = "命中" if results["7.1.4"].get(k) else "—"
            if a == b == "命中":
                both += 1
            elif a == "命中":
                only_new += 1
            elif b == "命中":
                only_old += 1
            print(f"{k:<24}{a:>8}{b:>8}")
        total = len(keys)
        print(f"\n两版本都命中: {both}；仅 7.1.5: {only_new}；仅 7.1.4: {only_old}；合计探针 {total}")
        print(f"7.1.5 检出 {sum(results['7.1.5'].values())}/{total}，7.1.4 检出 {sum(results['7.1.4'].values())}/{total}")
        json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "findings-versions.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
