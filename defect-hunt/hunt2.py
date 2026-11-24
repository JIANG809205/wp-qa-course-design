#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缺陷探测第二轮：修正误判 + 补充检查。"""

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


def record(cid, title, expect, actual, status, evidence=""):
    FINDINGS.append({"id": cid, "title": title, "expect": expect,
                     "actual": actual, "status": status, "evidence": evidence[:300]})
    print(f"[{status:<7}] {cid} {title} -> {actual}"
          + (f"  | {evidence[:70]}" if evidence else ""))


# 修正 CHK-06：用完整参数，验证的是权限而非参数校验
r = S.post(BASE + "/wp-json/wp/v2/users",
           json={"username": "hacker01", "email": "h@example.com",
                 "password": "Hack@2026", "roles": ["administrator"]},
           headers={"Authorization": AUTH}, timeout=20)
record("CHK-16", "作者身份创建管理员用户（完整参数）", "401/403",
       f"HTTP {r.status_code}", "PASS" if r.status_code in (401, 403) else "DEFECT", r.text[:200])

# 未认证读取评论：是否会泄漏待审核评论
r = S.get(BASE + "/wp-json/wp/v2/comments?per_page=100", timeout=20)
leak = False
detail = ""
if r.status_code == 200:
    try:
        items = r.json()
        stat = {i.get("status") for i in items}
        leak = any(s != "approved" for s in stat)
        detail = f"HTTP 200，共 {len(items)} 条，状态集合 {stat}"
    except Exception as e:  # noqa: BLE001
        detail = f"解析失败 {e}"
else:
    detail = f"HTTP {r.status_code}"
record("CHK-17", "未认证读取评论列表是否泄漏待审/垃圾评论", "仅 approved",
       detail, "DEFECT" if leak else "PASS", r.text[:200] if r.status_code == 200 else "")

# 调试日志是否可直接下载（WP_DEBUG_LOG=true 会生成 debug.log）
r = S.get(BASE + "/wp-content/debug.log", timeout=20)
leak = r.status_code == 200 and len(r.content) > 0
record("CHK-18", "调试日志 debug.log 是否可被匿名下载", "403/404",
       f"HTTP {r.status_code}，{len(r.content)} 字节",
       "DEFECT" if leak else "PASS", r.text[:200] if leak else "")

# wp-config.php 直接访问
r = S.get(BASE + "/wp-config.php", timeout=20)
record("CHK-19", "wp-config.php 直接访问", "空白/403，不输出内容",
       f"HTTP {r.status_code}，{len(r.content)} 字节",
       "DEFECT" if b"DB_PASSWORD" in r.content or b"table_prefix" in r.content else "PASS",
       r.text[:120])

# 超限文件上传（16M 上限，传 20M）
big = os.urandom(20 * 1024 * 1024)
r = S.post(BASE + "/wp-json/wp/v2/media",
           files={"file": ("big.jpg", big, "image/jpeg")},
           headers={"Authorization": AUTH}, timeout=60)
record("CHK-20", "上传 20MB 文件（超过 16M 限制）", "4xx 且提示大小超限，不应 5xx",
       f"HTTP {r.status_code}", "DEFECT" if r.status_code >= 500 else "PASS", r.text[:200])

# 中文文件名
png = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
r = S.post(BASE + "/wp-json/wp/v2/media",
           files={"file": ("测试图片.png", png, "image/png")},
           headers={"Authorization": AUTH}, timeout=30)
ok = r.status_code in (200, 201)
detail = f"HTTP {r.status_code}"
if ok:
    try:
        data = r.json()
        detail += f"，文件名={data.get('slug')}，URL 可访问={'是' if S.head(data['source_url'], timeout=10).status_code == 200 else '否'}"
    except Exception:  # noqa: BLE001
        pass
record("CHK-21", "中文文件名上传", "上传成功且可访问", detail, "PASS" if ok else "OBSERVE", r.text[:200])

# SQL 注入样式输入
r = S.get(BASE + "/?s=%27%20OR%201%3D1--", timeout=20)
record("CHK-22", "搜索框 SQL 注入样式输入", "不返回 5xx、不泄漏数据",
       f"HTTP {r.status_code}，返回 {len(r.content)} 字节",
       "DEFECT" if r.status_code >= 500 else "PASS", "")

# Server 头暴露版本
r = S.get(BASE + "/", timeout=20)
server = r.headers.get("Server", "")
record("CHK-23", "Server 响应头是否暴露版本号", "不应暴露具体版本",
       server or "未设置", "DEFECT" if "/" in server else "PASS", "")

# 目录遍历
r = S.get(BASE + "/wp-content/../wp-config.php", timeout=20)
record("CHK-24", "路径遍历尝试", "403/400/404",
       f"HTTP {r.status_code}", "PASS" if r.status_code in (400, 403, 404) else "OBSERVE", "")

ok_n = sum(1 for f in FINDINGS if f["status"] == "PASS")
df = sum(1 for f in FINDINGS if f["status"] == "DEFECT")
ob = sum(1 for f in FINDINGS if f["status"] == "OBSERVE")
print(f"\n第二轮 {len(FINDINGS)} 项：PASS {ok_n}，DEFECT {df}，OBSERVE {ob}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings2.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(FINDINGS, fh, ensure_ascii=False, indent=2)
print("已写入", out)
