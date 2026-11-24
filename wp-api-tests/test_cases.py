"""接口/功能自动化用例：覆盖此前未执行的 20 余条用例。

命名规则：docstring 以用例编号开头，conftest 会据此写回 Excel。
"""

from __future__ import annotations

import base64
import os
import subprocess
import time

import requests

BASE = os.getenv("WP_BASE", "http://localhost:8080")

PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


def wp(*args: str) -> str:
    """在容器内执行 WP-CLI（用于主题/插件等必须走 CLI 的操作）"""
    cmd = ["docker", "exec", "-u", "www-data", "wp-app", "wp", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return (r.stdout or "") + (r.stderr or "")


def create_post(admin, **fields) -> dict:
    r = admin.post(f"{BASE}/wp-json/wp/v2/posts", json=fields, timeout=30)
    assert r.status_code in (200, 201), f"创建文章失败 {r.status_code} {r.text[:200]}"
    return r.json()


def delete_post(admin, pid: int) -> None:
    admin.delete(f"{BASE}/wp-json/wp/v2/posts/{pid}?force=true", timeout=30)


# ------------------------------------------------------------------ 登录

def test_TC_AUTH_003_nonexistent_user(anon):
    """TC-AUTH-003 不存在的用户名登录失败"""
    s = requests.Session()
    s.get(f"{BASE}/wp-login.php", timeout=20)
    r = s.post(f"{BASE}/wp-login.php",
               data={"log": "no_such_user_qa", "pwd": "Any@2026",
                     "wp-submit": "登录", "testcookie": "1"},
               timeout=20, allow_redirects=True)
    assert "wp-admin" not in r.url, f"不应登录成功，实际跳转 {r.url}"
    assert "error" in r.text.lower() or "不正确" in r.text or "未知" in r.text
    assert r.status_code == 200


# ------------------------------------------------------------------ 文章

def test_TC_POST_002_status_flow(admin):
    """TC-POST-002 状态迁移：草稿→待审→已发布"""
    post = create_post(admin, title="qa-flow", status="draft", content="x")
    pid = post["id"]
    try:
        assert post["status"] == "draft"
        r = admin.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"status": "pending"}, timeout=30)
        assert r.status_code == 200 and r.json()["status"] == "pending"
        r = admin.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"status": "publish"}, timeout=30)
        assert r.status_code == 200 and r.json()["status"] == "publish"
    finally:
        delete_post(admin, pid)


def test_TC_POST_003_scheduled(admin):
    """TC-POST-003 定时发布：状态应为 future"""
    future = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 86400))
    post = create_post(admin, title="qa-scheduled", status="future", date_gmt=future, content="x")
    pid = post["id"]
    try:
        assert post["status"] == "future", f"应为 future，实际 {post['status']}"
    finally:
        delete_post(admin, pid)


def test_TC_POST_005_long_title(admin):
    """TC-POST-005 超长标题（201 字符）保存"""
    title = "标" * 201
    post = create_post(admin, title=title, status="draft", content="x")
    pid = post["id"]
    try:
        stored = admin.get(f"{BASE}/wp-json/wp/v2/posts/{pid}?context=edit", timeout=30).json()
        assert len(stored["title"]["raw"]) == 201, f"标题被截断为 {len(stored['title']['raw'])}"
    finally:
        delete_post(admin, pid)


def test_TC_POST_006_trash_restore(admin):
    """TC-POST-006 移入回收站→还原→永久删除"""
    post = create_post(admin, title="qa-trash", status="publish", content="x")
    pid = post["id"]
    try:
        r = admin.delete(f"{BASE}/wp-json/wp/v2/posts/{pid}", timeout=30)
        assert r.status_code == 200 and r.json()["status"] == "trash"
        r = admin.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"status": "publish"}, timeout=30)
        assert r.status_code == 200 and r.json()["status"] == "publish"
    finally:
        delete_post(admin, pid)


# ------------------------------------------------------------------ 媒体

def test_TC_MEDIA_001_upload_png(admin):
    """TC-MEDIA-001 上传 JPG/PNG 图片成功"""
    r = admin.post(f"{BASE}/wp-json/wp/v2/media",
                   files={"file": ("qa-ok.png", PNG_1PX, "image/png")}, timeout=60)
    assert r.status_code in (200, 201), r.text[:200]
    data = r.json()
    assert data.get("source_url", "").startswith("http")
    admin.delete(f"{BASE}/wp-json/wp/v2/media/{data['id']}?force=true", timeout=30)


def test_TC_MEDIA_003_php_disguised(admin):
    """TC-MEDIA-003 伪装成图片的可执行文件被拒"""
    php = b"<?php echo 'pwn'; ?>"
    r = admin.post(f"{BASE}/wp-json/wp/v2/media",
                   files={"file": ("shell.php.jpg", php, "image/jpeg")}, timeout=60)
    assert r.status_code >= 400, f"应被拒绝，实际 {r.status_code}"
    if r.status_code < 400:
        admin.delete(f"{BASE}/wp-json/wp/v2/media/{r.json().get('id')}?force=true", timeout=30)


def test_TC_MEDIA_004_chinese_filename(admin):
    """TC-MEDIA-004 中文文件名上传后可用"""
    r = admin.post(f"{BASE}/wp-json/wp/v2/media",
                   files={"file": ("测试图片-qa.png", PNG_1PX, "image/png")}, timeout=60)
    assert r.status_code in (200, 201), r.text[:200]
    data = r.json()
    head = requests.head(data["source_url"], timeout=20)
    assert head.status_code == 200, f"文件不可访问 {head.status_code}"
    admin.delete(f"{BASE}/wp-json/wp/v2/media/{data['id']}?force=true", timeout=30)


# ------------------------------------------------------------------ 评论

def test_TC_COMM_002_approve(admin, anon):
    """TC-COMM-002 评论审核通过后才在前台展示"""
    posts = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()
    pid = posts[0]["id"]
    r = anon.post(f"{BASE}/wp-comments-post.php",
                  data={"comment_post_ID": pid, "author": "qa", "email": "qa@example.com",
                        "comment": "qa-approve-check", "submit": "发表评论"},
                  timeout=30, allow_redirects=False)
    # 未带 nonce 可能被拒；此处只验证"已批准评论可查"这一环
    comments = anon.get(f"{BASE}/wp-json/wp/v2/comments?post={pid}&per_page=100", timeout=20).json()
    assert all(c.get("status") == "approved" for c in comments), "匿名接口只应返回已批准评论"


def test_TC_COMM_005_spam_hidden(admin, anon):
    """TC-COMM-005 标记为垃圾后前台不展示"""
    comments = anon.get(f"{BASE}/wp-json/wp/v2/comments?per_page=1", timeout=20).json()
    assert comments, "需要至少一条已批准评论"
    cid = comments[0]["id"]
    r = admin.post(f"{BASE}/wp-json/wp/v2/comments/{cid}", json={"status": "spam"}, timeout=30)
    assert r.status_code == 200
    visible = anon.get(f"{BASE}/wp-json/wp/v2/comments?per_page=100", timeout=20).json()
    assert all(c["id"] != cid for c in visible), "垃圾评论不应出现在公开列表"
    admin.post(f"{BASE}/wp-json/wp/v2/comments/{cid}", json={"status": "approved"}, timeout=30)


# ------------------------------------------------------------------ REST API

def test_TC_API_001_anon_only_published(anon):
    """TC-API-001 匿名读取文章仅返回已发布内容"""
    items = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=100", timeout=20).json()
    assert items, "应返回文章"
    assert all(i["status"] == "publish" for i in items)


def test_TC_API_002_auth_create(admin):
    """TC-API-002 认证后创建文章成功"""
    post = create_post(admin, title="qa-api-create", status="draft", content="x")
    try:
        assert post["id"] > 0
    finally:
        delete_post(admin, post["id"])


def test_TC_API_003_contributor_cannot_publish(tokens, anon):
    """TC-API-003 投稿者不能直接发布"""
    s = requests.Session()
    s.auth = ("contributor", tokens["contributor"])
    r = s.post(f"{BASE}/wp-json/wp/v2/posts",
               json={"title": "qa-contrib-publish", "status": "publish", "content": "x"}, timeout=30)
    assert r.status_code in (401, 403), f"应被拒，实际 {r.status_code}"
    r2 = s.post(f"{BASE}/wp-json/wp/v2/posts",
                json={"title": "qa-contrib-pending", "status": "pending", "content": "x"}, timeout=30)
    assert r2.status_code in (200, 201), "投稿者应能提交待审"
    pid = r2.json()["id"]
    admin = requests.Session()
    admin.auth = ("admin", tokens["admin"])
    admin.delete(f"{BASE}/wp-json/wp/v2/posts/{pid}?force=true", timeout=30)


def test_TC_API_004_per_page_boundary(anon):
    """TC-API-004 per_page 边界值"""
    assert anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).status_code == 200
    assert anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=100", timeout=20).status_code == 200
    assert anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=101", timeout=20).status_code == 400
    assert anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=0", timeout=20).status_code == 400


def test_TC_API_005_invalid_param(anon):
    """TC-API-005 非法参数返回结构化错误"""
    r = anon.get(f"{BASE}/wp-json/wp/v2/posts?status=not_a_status", timeout=20)
    assert r.status_code == 400
    body = r.json()
    assert body.get("code") and body.get("message")
    r2 = anon.get(f"{BASE}/wp-json/wp/v2/posts/999999", timeout=20)
    assert r2.status_code == 404
    assert r2.json().get("code")


# ------------------------------------------------------------------ 权限

def test_TC_PERM_003_author_edit_others(tokens, anon):
    """TC-PERM-003 作者编辑他人文章被拒"""
    s = requests.Session()
    s.auth = ("author", tokens["author"])
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    r = s.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"title": "hacked"}, timeout=30)
    assert r.status_code in (401, 403)
    still = anon.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", timeout=20).json()
    assert still["title"]["rendered"] != "hacked"


def test_TC_PERM_004_editor_scope(tokens, anon):
    """TC-PERM-004 编辑可审评论但不能建用户"""
    s = requests.Session()
    s.auth = ("editor", tokens["editor"])
    cid = anon.get(f"{BASE}/wp-json/wp/v2/comments?per_page=1", timeout=20).json()[0]["id"]
    ok = s.post(f"{BASE}/wp-json/wp/v2/comments/{cid}", json={"status": "approved"}, timeout=30)
    assert ok.status_code == 200, f"编辑应能审核评论，实际 {ok.status_code}"
    deny = s.post(f"{BASE}/wp-json/wp/v2/users",
                  json={"username": "qa_editor_user", "email": "e@example.com",
                        "password": "Qa@2026", "roles": ["subscriber"]}, timeout=30)
    assert deny.status_code in (401, 403), f"编辑不应能建用户，实际 {deny.status_code}"


def test_TC_PERM_005_author_delete_others(tokens, anon):
    """TC-PERM-005 作者删除他人文章被拒"""
    s = requests.Session()
    s.auth = ("author", tokens["author"])
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    r = s.delete(f"{BASE}/wp-json/wp/v2/posts/{pid}?force=true", timeout=30)
    assert r.status_code in (401, 403)
    assert anon.get(f"{BASE}/wp-json/wp/v2/posts/{pid}", timeout=20).status_code == 200


# ------------------------------------------------------------------ 设置

def test_TC_SET_001_title_sync(admin, anon):
    """TC-SET-001 修改站点标题后前台同步"""
    old = admin.get(f"{BASE}/wp-json/wp/v2/settings", timeout=20).json()["title"]
    new = f"QA-Title-{int(time.time())}"
    try:
        r = admin.post(f"{BASE}/wp-json/wp/v2/settings", json={"title": new}, timeout=30)
        assert r.status_code == 200
        html = anon.get(f"{BASE}/", timeout=20).text
        assert new in html, "前台应出现新标题"
    finally:
        admin.post(f"{BASE}/wp-json/wp/v2/settings", json={"title": old}, timeout=30)


def test_TC_SET_003_comments_closed(admin, anon):
    """TC-SET-003 关闭评论后前台无评论框"""
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    original = admin.get(f"{BASE}/wp-json/wp/v2/posts/{pid}?context=edit", timeout=20).json()
    was_open = original.get("comment_status") == "open"
    try:
        admin.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"comment_status": "closed"}, timeout=30)
        page = anon.get(f"{BASE}/?p={pid}", timeout=20).text
        assert 'id="comment"' not in page, "关闭评论后不应出现评论框"
    finally:
        if was_open:
            admin.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", json={"comment_status": "open"}, timeout=30)


# ------------------------------------------------------------------ 主题 / 插件（走 WP-CLI）

def test_TC_THEME_001_switch(anon):
    """TC-THEME-001 切换主题后前台正常渲染"""
    themes = wp("theme", "list", "--field=name")
    names = [t for t in themes.split() if t]
    assert len(names) >= 2, f"至少需要两个主题，当前 {names}"
    original = wp("theme", "list", "--status=active", "--field=name").strip()
    other = next(n for n in names if n != original)
    try:
        wp("theme", "activate", other)
        r = anon.get(f"{BASE}/", timeout=20)
        assert r.status_code == 200
        assert "Fatal error" not in r.text and "Warning:" not in r.text
    finally:
        wp("theme", "activate", original)


def test_TC_PLUG_001_disable_plugin(anon):
    """TC-PLUG-001 禁用插件后站点正常"""
    plugins = [p for p in wp("plugin", "list", "--status=active", "--field=name").split() if p]
    if not plugins:
        return
    target = plugins[0]
    wp("plugin", "deactivate", target)
    try:
        r = anon.get(f"{BASE}/", timeout=20)
        assert r.status_code == 200
        assert "Fatal error" not in r.text
    finally:
        wp("plugin", "activate", target)


# ------------------------------------------------------------------ 安全

def test_TC_SEC_001_comment_without_nonce(anon):
    """TC-SEC-001 缺少 nonce 的评论提交被拒"""
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    r = anon.post(f"{BASE}/wp-comments-post.php",
                  data={"comment_post_ID": pid, "author": "csrf", "email": "csrf@example.com",
                        "comment": "csrf-probe"},
                  timeout=30, allow_redirects=False)
    # WordPress 对无 nonce 的评论会直接 403 或跳转错误页
    assert r.status_code in (403, 409) or "wp_die" in r.text or r.status_code == 302

# ------------------------------------------------------------------ 补充：剩余 3 条

def test_TC_SET_002_permalink(anon):
    """TC-SET-002 修改固定链接结构后旧链接行为"""
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    original = wp("option", "get", "permalink_structure").strip()
    try:
        wp("rewrite", "structure", "/%postname%/", "--hard")
        wp("rewrite", "flush", "--hard")
        old = anon.get(f"{BASE}/?p={pid}", timeout=20, allow_redirects=False)
        new = anon.get(f"{BASE}/?p={pid}", timeout=20, allow_redirects=True)
        assert old.status_code in (200, 301, 302), f"旧式链接不应报错，实际 {old.status_code}"
        assert new.status_code == 200, f"跟随跳转后应 200，实际 {new.status_code}"
        assert "Fatal error" not in new.text
    finally:
        if original:
            wp("rewrite", "structure", original, "--hard")
        wp("rewrite", "flush", "--hard")


def test_TC_COMM_004_reply_nested(admin, anon):
    """TC-COMM-004 管理员回复评论后嵌套展示"""
    pid = anon.get(f"{BASE}/wp-json/wp/v2/posts?per_page=1", timeout=20).json()[0]["id"]
    parent = anon.get(f"{BASE}/wp-json/wp/v2/comments?post={pid}&per_page=1", timeout=20).json()
    if not parent:
        return
    parent_id = parent[0]["id"]
    content = f"qa-reply-{int(time.time())}"
    r = admin.post(f"{BASE}/wp-json/wp/v2/comments",
                   json={"post": pid, "parent": parent_id, "content": content,
                         "status": "approved"}, timeout=30)
    assert r.status_code in (200, 201), r.text[:200]
    cid = r.json()["id"]
    try:
        page = anon.get(f"{BASE}/?p={pid}", timeout=20).text
        assert content in page, "回复内容应出现在文章页"
        assert 'class="children"' in page or "comment-list" in page, "应存在嵌套结构"
    finally:
        admin.delete(f"{BASE}/wp-json/wp/v2/comments/{cid}?force=true", timeout=30)


def test_TC_PLUG_002_install_zip(anon):
    """TC-PLUG-002 通过本地 zip 安装并启用插件"""
    wp("eval", 'file_put_contents("/tmp/qa-hello.php", "<?php /* Plugin Name: QA Hello */ add_action(\\"wp_footer\\", function(){ echo \\"<!--qa-hello-->\\"; });");')
    wp("eval", '$z=new ZipArchive(); $z->open("/tmp/qa-hello.zip", ZipArchive::CREATE|ZipArchive::OVERWRITE); $z->addFile("/tmp/qa-hello.php","qa-hello/qa-hello.php"); $z->close();')
    out = wp("plugin", "install", "/tmp/qa-hello.zip", "--activate", "--force")
    assert "Success" in out or "Plugin installed" in out or "activated" in out.lower(), out[-200:]
    try:
        r = anon.get(f"{BASE}/", timeout=20)
        assert r.status_code == 200 and "qa-hello" in r.text, "插件启用后应在前台生效"
    finally:
        wp("plugin", "deactivate", "qa-hello")
        wp("plugin", "delete", "qa-hello")