#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深挖两个疑点：投稿者能否看到他人评论；重名建用户为何 500。"""

from __future__ import annotations

import re

import requests

BASE = "http://localhost:8080"
PWD = {"admin": "Admin@2026", "contributor": "Contributor@2026", "author": "Author@2026"}


def login(role):
    s = requests.Session()
    s.get(f"{BASE}/wp-login.php", timeout=20)
    s.post(f"{BASE}/wp-login.php",
           data={"log": role, "pwd": PWD[role], "wp-submit": "登录", "testcookie": "1"},
           timeout=20, allow_redirects=True)
    return s


def nonce(s):
    html = s.get(f"{BASE}/wp-admin/", timeout=20).text
    m = re.search(r'"nonce"\s*:\s*"([a-f0-9]+)"', html)
    return m.group(1) if m else ""


for role in ("contributor", "author"):
    s = login(role)
    r = s.get(f"{BASE}/wp-admin/edit-comments.php", timeout=25)
    body = r.text
    rows = len(re.findall(r'<tr[^>]*id="comment-\d+"', body))
    approve = body.count("批准") + body.count("approve")
    bulk = "bulk-action" in body or "批量操作" in body
    empty = ("暂无评论" in body) or ("没有找到" in body)
    print(f"\n--- {role} 访问评论列表")
    print(f"    status={r.status_code}  评论行数={rows}  '批准'出现={approve}  批量操作={bulk}  空列表提示={empty}")
    m = re.search(r"共\s*(\d+)\s*条", body)
    print(f"    页面统计: {m.group(0) if m else '未找到'}")

# 重名建用户
s = login("admin")
n = nonce(s)
for attempt in (1, 2):
    r = s.post(BASE + "/wp-json/wp/v2/users", headers={"X-WP-Nonce": n},
               json={"username": "dup_probe", "email": "dup@example.com",
                     "password": "Dup@2026", "roles": ["subscriber"]}, timeout=30)
    print(f"\n--- admin 创建同名用户 第{attempt}次: {r.status_code}")
    print("    ", r.text[:220])

# 作者改他人文章（接口）确认 403 的语义
s = login("author")
n = nonce(s)
posts = requests.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()
pid = posts[0]["id"]
r = s.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", headers={"X-WP-Nonce": n},
           json={"title": "author-try"}, timeout=30)
print(f"\n--- author 修改他人文章(id={pid}): {r.status_code} {r.text[:160]}")
