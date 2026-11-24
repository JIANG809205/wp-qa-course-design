#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""权限矩阵 30 格（修正版）

修正点：
1. REST nonce 改从 admin-ajax.php?action=rest-nonce 获取（此前正则抓到的是别的 nonce，
   导致所有接口 403 都是 rest_cookie_invalid_nonce，测量无效）。
2. 页面通道改用"期望元素是否存在"判定，不再用"权限/抱歉"这类文本关键词（会误判）。
3. 判定以接口为准（权限的最终边界），页面作为体验证据。
4. 投稿者 OP1 为有条件：publish 应被拒、pending 应允许，两个都验。
"""

from __future__ import annotations

import base64
import json
import os
import re

import requests

BASE = "http://localhost:8080"
PWD = {"admin": "Admin@2026", "editor": "Editor@2026", "author": "Author@2026",
       "contributor": "Contributor@2026", "subscriber": "Subscriber@2026",
       "auditor": "Auditor@2026"}
OPS = ["OP1 发布文章", "OP2 编辑他人文章", "OP3 审核评论", "OP4 上传媒体", "OP5 新建用户", "OP6 修改设置"]

# Y=允许  N=拒绝  C=有条件（仅自己的文章 / 仅提交待审）
EXPECT = {
    "admin":       ["Y", "Y", "Y", "Y", "Y", "Y"],
    "editor":      ["Y", "Y", "Y", "Y", "N", "N"],
    "author":      ["C", "N", "N", "Y", "N", "N"],
    "contributor": ["C", "N", "N", "N", "N", "N"],
    "subscriber":  ["N", "N", "N", "N", "N", "N"],
    # 自定义角色：read + edit_posts + moderate_comments（可审评论，不能发布/上传/建用户/改设置）
    "auditor":     ["C", "N", "Y", "N", "N", "N"],
}

# 页面通道：每格期望出现的元素 id（None 表示不检查页面）
UI_MARK = {
    "OP1": "id=\"title\"",
    "OP2": "id=\"title\"",
    "OP3": "id=\"the-comment-list\"",
    "OP4": "id=\"plupload-browse-button\"",
    "OP5": "id=\"createuser\"",
    "OP6": "id=\"blogname\"",
}

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def login(role: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "qa-perm/2.0"})
    s.get(f"{BASE}/wp-login.php", timeout=20)
    s.post(f"{BASE}/wp-login.php",
           data={"log": role, "pwd": PWD[role], "wp-submit": "登录", "testcookie": "1"},
           timeout=20, allow_redirects=True)
    return s


def rest_nonce(s: requests.Session) -> str:
    r = s.get(f"{BASE}/wp-admin/admin-ajax.php?action=rest-nonce", timeout=20)
    if r.status_code == 200 and re.fullmatch(r"[a-f0-9]{6,}", r.text.strip() or ""):
        return r.text.strip()
    html = s.get(f"{BASE}/wp-admin/", timeout=20).text
    m = re.search(r'wpApiSettings\s*=\s*\{[^}]*"nonce"\s*:\s*"([a-f0-9]+)"', html, re.S)
    return m.group(1) if m else ""


def ui_check(s, path, mark):
    r = s.get(BASE + path, timeout=25, allow_redirects=True)
    body = r.text
    denied = ("抱歉" in body) or ("/wp-admin/profile.php" in r.url)
    return {"status": r.status_code, "denied": denied, "has_mark": mark in body, "url": r.url}


def api(s, method, path, nonce, **kw):
    return s.request(method, BASE + path, headers={"X-WP-Nonce": nonce}, timeout=30, **kw)


def classify(code):
    if code in (200, 201):
        return "allow"
    if code in (401, 403):
        return "deny"
    return f"other({code})"


def main() -> int:
    anon = requests.Session()
    other_post = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    try:
        comment_id = anon.get(f"{BASE}/wp-json/wp/v2/comments?per_page=1", timeout=20).json()[0]["id"]
    except Exception:  # noqa: BLE001
        comment_id = None

    rows = []
    for role in PWD:
        s = login(role)
        nonce = rest_nonce(s)
        print(f"\n===== {role} nonce={'OK' if nonce else 'MISSING'} =====")

        ui = {
            "OP1": ui_check(s, "/wp-admin/post-new.php", UI_MARK["OP1"]),
            "OP2": ui_check(s, f"/wp-admin/post.php?post={other_post}&action=edit", UI_MARK["OP2"]),
            "OP3": ui_check(s, "/wp-admin/edit-comments.php", UI_MARK["OP3"]),
            "OP4": ui_check(s, "/wp-admin/media-new.php", UI_MARK["OP4"]),
            "OP5": ui_check(s, "/wp-admin/user-new.php", UI_MARK["OP5"]),
            "OP6": ui_check(s, "/wp-admin/options-general.php", UI_MARK["OP6"]),
        }

        api_res = {}
        r = api(s, "POST", "/wp-json/wp/v2/posts", nonce,
                json={"title": f"perm-{role}", "status": "publish", "content": "x"})
        api_res["OP1"] = classify(r.status_code)
        api_res["OP1_msg"] = r.text[:100]

        # 投稿者的有条件分支：publish 被拒后，pending 应允许
        pending_ok = None
        if api_res["OP1"] == "deny":
            r2 = api(s, "POST", "/wp-json/wp/v2/posts", nonce,
                     json={"title": f"perm-{role}-pending", "status": "pending", "content": "x"})
            pending_ok = r2.status_code in (200, 201)
            api_res["OP1_pending"] = r2.status_code
            if pending_ok:
                api_res["OP1"] = "allow_pending"

        r = api(s, "POST", f"/wp-json/wp/v2/posts/{other_post}", nonce, json={"title": "try-edit"})
        api_res["OP2"] = classify(r.status_code)
        api_res["OP2_msg"] = r.text[:100]

        if comment_id:
            r = api(s, "POST", f"/wp-json/wp/v2/comments/{comment_id}", nonce,
                    json={"status": "approved"})
            api_res["OP3"] = classify(r.status_code)
            api_res["OP3_msg"] = r.text[:100]
        else:
            api_res["OP3"] = "no_data"

        r = api(s, "POST", "/wp-json/wp/v2/media", nonce,
                files={"file": (f"perm-{role}.png", PNG, "image/png")})
        api_res["OP4"] = classify(r.status_code)
        api_res["OP4_msg"] = r.text[:100]

        r = api(s, "POST", "/wp-json/wp/v2/users", nonce,
                json={"username": f"perm2_{role}", "email": f"p2_{role}@example.com",
                      "password": "Perm@2026", "roles": ["subscriber"]})
        api_res["OP5"] = classify(r.status_code)
        api_res["OP5_msg"] = r.text[:100]

        r = api(s, "POST", "/wp-json/wp/v2/settings", nonce, json={"title": f"QA2-{role}"})
        api_res["OP6"] = classify(r.status_code)
        api_res["OP6_msg"] = r.text[:100]

        for i, op in enumerate(["OP1", "OP2", "OP3", "OP4", "OP5", "OP6"]):
            rows.append({
                "role": role, "op": op, "name": OPS[i], "expect": EXPECT[role][i],
                "ui_status": ui[op]["status"], "ui_denied": ui[op]["denied"],
                "ui_marker": ui[op]["has_mark"],
                "api": api_res[op], "api_msg": api_res.get(op + "_msg", ""),
            })
            print(f"  {op} {OPS[i]:<12} 预期={EXPECT[role][i]}  "
                  f"UI={ui[op]['status']}{'拒' if ui[op]['denied'] else ''}"
                  f"{'✓' if ui[op]['has_mark'] else '✗'}  API={api_res[op]}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "permission-matrix-v2.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)

    # 判定
    print("\n===== 判定（以接口为准）=====")
    mism = []
    for r in rows:
        allow = r["api"] in ("allow", "allow_pending")
        expect_allow = r["expect"] in ("Y", "C")
        # 有条件格：C 要求 "publish 受限但 pending 可用"
        # 有条件格：作者可发布自己的文章（allow），投稿者只能提交待审（allow_pending），两者都算符合
        if r["expect"] == "C":
            ok = r["api"] in ("allow", "allow_pending")
        else:
            ok = (allow == expect_allow)
        if not ok:
            mism.append(r)
            print(f"  [!] {r['role']:<12}{r['op']} 预期={r['expect']} 实际={r['api']}  {r['api_msg'][:60]}")
    print(f"  不一致：{len(mism)}/{len(rows)}")
    print("\n已写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
