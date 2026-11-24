#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核实 4 个不一致格子：到底是系统缺陷还是判据问题。"""

from __future__ import annotations

import json
import os
import re

import requests

BASE = "http://localhost:8080"
ROLES = {"admin": "Admin@2026", "editor": "Editor@2026", "author": "Author@2026",
         "contributor": "Contributor@2026", "subscriber": "Subscriber@2026"}

MARKS = ["抱歉", "不能访问", "wp_die", "无权", "权限不足"]


def login(role):
    s = requests.Session()
    s.get(f"{BASE}/wp-login.php", timeout=20)
    s.post(f"{BASE}/wp-login.php",
           data={"log": role, "pwd": ROLES[role], "wp-submit": "登录", "testcookie": "1"},
           timeout=20, allow_redirects=True)
    return s


def nonce(s):
    html = s.get(f"{BASE}/wp-admin/", timeout=20).text
    m = re.search(r'"nonce"\s*:\s*"([a-f0-9]+)"', html)
    return m.group(1) if m else ""


def show(role, path, marker_id):
    s = login(role)
    r = s.get(BASE + path, timeout=25)
    body = r.text
    marks = [m for m in MARKS if m in body]
    print(f"\n--- {role} GET {path}")
    print(f"    status={r.status_code} url={r.url}")
    print(f"    命中拒绝标记={marks or '无'}")
    print(f"    期望元素 {marker_id}: {'存在' if marker_id in body else '缺失'}")
    title = re.search(r"<title>(.*?)</title>", body, re.S)
    print(f"    title={(title.group(1).strip()[:60] if title else '无')}")
    return s


s = show("admin", "/wp-admin/user-new.php", 'id="createuser"')
n = nonce(s)
r = s.post(BASE + "/wp-json/wp/v2/users", headers={"X-WP-Nonce": n},
           json={"username": "perm_probe_admin", "email": "probe@example.com",
                 "password": "Probe@2026", "roles": ["subscriber"]}, timeout=30)
print(f"    admin 创建用户 API: {r.status_code} {r.text[:200]}")

show("author", "/wp-admin/edit-comments.php", 'id="the-comment-list"')
show("contributor", "/wp-admin/post-new.php", 'id="title"')
show("contributor", "/wp-admin/edit-comments.php", 'id="the-comment-list"')
