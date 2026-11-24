#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缺陷探测：对 WordPress 逐项发起可复现的检查，记录实际响应作为证据。

每个检查输出 PASS（符合预期）/ DEFECT（确认异常）/ OBSERVE（记为风险，需人工判定）。
"""

from __future__ import annotations

import base64
import json
import os

import requests

BASE = "http://localhost:8080"
APP_PASS = os.getenv("APP_PASS", "XEGi7fGumRRl8PJmbE7RDRMx")
AUTH = "Basic " + base64.b64encode(f"author:{APP_PASS}".encode()).decode()

S = requests.Session()
S.headers.update({"User-Agent": "qa-defect-hunt/1.0"})

FINDINGS = []


def record(check_id, title, expect, actual, status, evidence=""):
    FINDINGS.append({
        "id": check_id, "title": title, "expect": expect,
        "actual": actual, "status": status, "evidence": evidence[:300],
    })
    print(f"[{status:<7}] {check_id} {title} -> {actual}" + (f"  | {evidence[:80]}" if evidence else ""))


def get(path, **kw):
    return S.get(BASE + path, timeout=20, allow_redirects=False, **kw)


# ---------------------------------------------------------------- API 参数校验

r = get("/wp-json/wp/v2/posts?per_page=101")
record("CHK-01", "REST per_page 超过上限", "400/限制为100", f"HTTP {r.status_code}",
       "PASS" if r.status_code == 400 else "DEFECT", r.text[:200])

r = get("/wp-json/wp/v2/posts?per_page=0")
record("CHK-02", "REST per_page=0", "400 或使用默认值", f"HTTP {r.status_code}",
       "PASS" if r.status_code in (400, 200) else "DEFECT", r.text[:200])

r = get("/wp-json/wp/v2/posts?status=not_a_status")
record("CHK-03", "REST 非法 status 参数", "400 且返回结构化错误", f"HTTP {r.status_code}",
       "PASS" if r.status_code == 400 else "DEFECT", r.text[:200])

r = get("/wp-json/wp/v2/posts?per_page=1")
try:
    items = r.json()
    has_draft = any(i.get("status") != "publish" for i in items)
    record("CHK-04", "匿名读取文章列表是否泄漏非公开内容", "仅 publish",
           "仅 publish" if not has_draft else "包含非 publish", "PASS" if not has_draft else "DEFECT",
           json.dumps([i.get("status") for i in items]))
except Exception as e:  # noqa: BLE001
    record("CHK-04", "匿名读取文章列表", "JSON", f"解析失败 {e}", "DEFECT")

# ---------------------------------------------------------------- 权限

r = S.post(BASE + "/wp-json/wp/v2/posts", json={"title": "x"}, timeout=20)
record("CHK-05", "匿名创建文章", "401", f"HTTP {r.status_code}",
       "PASS" if r.status_code == 401 else "DEFECT", r.text[:200])

r = S.post(BASE + "/wp-json/wp/v2/users", json={"username": "hacker", "password": "x"},
           headers={"Authorization": AUTH}, timeout=20)
record("CHK-06", "作者身份创建用户", "401/403", f"HTTP {r.status_code}",
       "PASS" if r.status_code in (401, 403) else "DEFECT", r.text[:200])

r = S.get(BASE + "/wp-json/wp/v2/users", timeout=20)
exposed = []
if r.status_code == 200:
    for u in r.json():
        exposed.extend(u.keys())
record("CHK-07", "未认证读取用户列表", "不应暴露内部字段",
       f"HTTP {r.status_code}，字段 {sorted(set(exposed))}", "OBSERVE", r.text[:200])

# ---------------------------------------------------------------- 安全响应头

r = get("/")
missing = [h for h in ("X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy")
           if h not in r.headers]
record("CHK-08", "安全响应头", "应设置常见安全头",
       f"缺失 {missing}" if missing else "齐全",
       "DEFECT" if len(missing) >= 2 else "PASS", str(dict(r.headers))[:300])

# ---------------------------------------------------------------- XSS / 输入处理

payload = "<script>alert(1)</script>"
r = get("/?s=" + payload)
reflected = payload in r.text
record("CHK-09", "搜索框 XSS 反射", "脚本标签被转义",
       "未转义反射" if reflected else "已转义/未反射",
       "DEFECT" if reflected else "PASS", r.text[:200])

long_q = "a" * 5000
r = get("/?s=" + long_q)
record("CHK-10", "搜索超长关键词", "不返回 5xx", f"HTTP {r.status_code}",
       "DEFECT" if r.status_code >= 500 else "PASS", "")

# ---------------------------------------------------------------- 上传校验

def upload(name, content, mime):
    files = {"file": (name, content, mime)}
    return S.post(BASE + "/wp-json/wp/v2/media", files=files,
                  headers={"Authorization": AUTH}, timeout=30)


r = upload("empty.png", b"", "image/png")
record("CHK-11", "上传 0 字节文件", "400 拒绝", f"HTTP {r.status_code}",
       "DEFECT" if r.status_code in (200, 201) else "PASS", r.text[:200])

r = upload("shell.php.jpg", b"<?php echo 1; ?>", "image/jpeg")
ok = r.status_code in (200, 201)
record("CHK-12", "上传伪装成 jpg 的 php 文件", "400 拒绝", f"HTTP {r.status_code}",
       "DEFECT" if ok else "PASS", r.text[:200])

# ---------------------------------------------------------------- 目录与入口

r = get("/wp-content/uploads/")
record("CHK-13", "上传目录是否可列目录", "403/404",
       f"HTTP {r.status_code}", "DEFECT" if r.status_code == 200 and "Index of" in r.text else "PASS", "")

r = S.post(BASE + "/xmlrpc.php", data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>',
           timeout=20)
record("CHK-14", "XML-RPC 是否开放", "建议关闭（可被用于暴力破解/放大攻击）",
       f"HTTP {r.status_code}", "OBSERVE" if r.status_code == 200 and "methodResponse" in r.text else "PASS",
       r.text[:200])

# ---------------------------------------------------------------- 登录暴力破解

r = S.post(BASE + "/wp-login.php", data={"log": "admin", "pwd": "wrong-1", "wp-submit": "登录",
                                         "testcookie": "1"}, timeout=20, allow_redirects=False)
codes = []
for i in range(5):
    resp = S.post(BASE + "/wp-login.php", data={"log": "admin", "pwd": f"wrong-{i}",
                                                "wp-submit": "登录", "testcookie": "1"},
                  timeout=20, allow_redirects=False)
    codes.append(resp.status_code)
locked = any(c in (429,) for c in codes)
record("CHK-15", "连续 6 次错误密码是否触发限制", "应出现锁定/验证码/429",
       f"连续返回 {codes}，无锁定", "DEFECT" if not locked else "PASS", "")

# ---------------------------------------------------------------- 输出

ok = [f for f in FINDINGS if f["status"] == "PASS"]
df = [f for f in FINDINGS if f["status"] == "DEFECT"]
ob = [f for f in FINDINGS if f["status"] == "OBSERVE"]

print(f"\n合计 {len(FINDINGS)} 项：PASS {len(ok)}，DEFECT {len(df)}，OBSERVE {len(ob)}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(FINDINGS, fh, ensure_ascii=False, indent=2)
print("已写入", out)
