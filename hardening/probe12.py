#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12 项安全探针：输出命中/未命中与证据，用于修复前后对照。

用法：python probe12.py <base_url> <out.json>
"""
from __future__ import annotations

import json
import sys

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/probe12.json"
PW = ""
try:
    PW = open("/tmp/wp_pass/admin.txt", encoding="utf-8").read().strip()
except OSError:
    pass

S = requests.Session()
S.headers.update({"User-Agent": "qa-probe/1.0"})
res = []


def add(pid, name, hit, evidence):
    res.append({"id": pid, "name": name, "hit": bool(hit), "evidence": evidence})
    print(f"{pid} {name:<18} {'命中' if hit else '未命中'}  {evidence[:70]}")


def g(path, **kw):
    return S.get(BASE + path, timeout=20, allow_redirects=False, **kw)


# P01 安全响应头
r = g("/")
hd = {k.lower(): v for k, v in r.headers.items()}
need = ["x-frame-options", "x-content-type-options", "referrer-policy", "permissions-policy"]
missing = [h for h in need if h not in hd]
add("P01", "安全响应头", len(missing) > 0, f"缺失 {len(missing)}/4：{','.join(missing) or '无'}")

# P02 debug.log
r = g("/wp-content/debug.log")
add("P02", "debug.log 可下载", r.status_code == 200, f"HTTP {r.status_code}, {len(r.content)} 字节")

# P03 上传目录索引
r = g("/wp-content/uploads/")
add("P03", "上传目录可列", r.status_code == 200 and b"Index of" in r.content, f"HTTP {r.status_code}")

# P04 readme.html
r = g("/readme.html")
add("P04", "readme.html 可访问", r.status_code == 200, f"HTTP {r.status_code}")

# P05 XML-RPC
r = S.post(BASE + "/xmlrpc.php", timeout=20,
           data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>',
           headers={"Content-Type": "text/xml"})
add("P05", "XML-RPC 可用", r.status_code == 200 and b"methodResponse" in r.content, f"HTTP {r.status_code}")

# P06 作者枚举
r = g("/?author=1")
loc = r.headers.get("Location", "")
add("P06", "作者枚举", r.status_code in (301, 302) and "/author/" in loc, f"HTTP {r.status_code} -> {loc[:40]}")

# P07 REST 用户匿名可读
r = g("/wp-json/wp/v2/users")
n = 0
try:
    n = len(r.json()) if isinstance(r.json(), list) else 0
except Exception:
    n = 0
add("P07", "REST 用户可枚举", r.status_code == 200 and n > 0, f"HTTP {r.status_code}, {n} 个用户")

# P08 空文件上传
auth = ("admin", PW) if PW else None
r = S.post(BASE + "/wp-json/wp/v2/media", auth=auth, timeout=30,
           files={"file": ("empty.png", b"", "image/png")})
add("P08", "空文件上传 500", r.status_code >= 500, f"HTTP {r.status_code}")

# P09 重复用户名
r = S.post(BASE + "/wp-json/wp/v2/users", auth=auth, timeout=30,
           json={"username": "admin", "password": "Xx123456!", "email": "dup@example.com"})
add("P09", "重名用户 500", r.status_code >= 500, f"HTTP {r.status_code}")

# P10 登录无锁定
codes = []
for i in range(6):
    rr = S.post(BASE + "/wp-login.php", timeout=20,
                data={"log": "admin", "pwd": f"wrong-{i}", "wp-submit": "Log In", "testcookie": "1"})
    codes.append(rr.status_code)
add("P10", "登录无失败限制", all(c in (200,) for c in codes), f"6 次状态码 {codes}")

# P11 非法参数
r = g("/wp-json/wp/v2/posts?per_page=abc")
add("P11", "非法参数 500", r.status_code >= 500, f"HTTP {r.status_code}")

# P12 license.txt
r = g("/license.txt")
add("P12", "license.txt 可访问", r.status_code == 200, f"HTTP {r.status_code}")

hits = sum(1 for x in res if x["hit"])
print(f"\n共 {len(res)} 项，命中 {hits} 项，未命中 {len(res)-hits} 项")
json.dump({"base": BASE, "hits": hits, "total": len(res), "items": res},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写入", OUT)
