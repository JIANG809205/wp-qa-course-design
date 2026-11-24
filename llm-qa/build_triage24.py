# -*- coding: utf-8 -*-
"""合并出 24 条归因样本（每类 8 条）。"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(BASE, "data", "failure_logs_hard.json")
dst = os.path.join(BASE, "data", "triage24.json")

existing = json.load(open(src, encoding="utf-8"))

new = [
    {"id": "E-05", "case": "并发压测", "gold": "环境问题",
     "log": "30 并发请求首页出现 502 Bad Gateway；Apache error.log 显示 server reached MaxRequestWorkers setting；单并发无异常。"},
    {"id": "E-06", "case": "CI 执行", "gold": "环境问题",
     "log": "java.net.UnknownHostException: localhost: Temporary failure in name resolution，发生在容器内执行测试时；宿主机 curl 同一地址正常。"},
    {"id": "E-07", "case": "TC-MEDIA-001", "gold": "环境问题",
     "log": "上传图片返回 500，PHP 日志 Warning: file_put_contents(): Write of 2048 bytes failed with errno=28 No space left on device；df -h 显示 /var 使用率 100%。"},
    {"id": "E-08", "case": "TC-SET-001", "gold": "环境问题",
     "log": "修改站点标题后前台仍显示旧值，约 60 秒后自动恢复；期间后台已显示新标题，对象缓存 TTL 为 60 秒。"},
    {"id": "S-05", "case": "TC-POST-001", "gold": "脚本问题",
     "log": "NoSuchElementException: Unable to locate element: #title；页面加载在 iframe#editor-canvas 内，脚本未执行 switchTo().frame()。"},
    {"id": "S-06", "case": "TC-COMM-002", "gold": "脚本问题",
     "log": "间歇性 TimeoutException（约 3/10 次），等待条件 presenceOfElementLocated(#comments)；单独重跑通过，失败截图显示页面仍在加载。"},
    {"id": "S-07", "case": "TC-AUTH-001", "gold": "脚本问题",
     "log": "创建用户返回 400 rest_invalid_param，message 为 username 已存在；该用户名来自上次未清理的测试数据。"},
    {"id": "S-08", "case": "TC-PERM-001", "gold": "脚本问题",
     "log": "AssertionError: expected [草案] but found [草稿]；断言中的状态文案与后台实际文案不一致。"},
    {"id": "D-05", "case": "探索性", "gold": "系统缺陷",
     "log": "GET / 响应头仅含 Date、Server、Content-Type、Link；缺少 X-Frame-Options、X-Content-Type-Options、Referrer-Policy、Permissions-Policy。"},
    {"id": "D-06", "case": "探索性", "gold": "系统缺陷",
     "log": "POST /xmlrpc.php，body 为 system.listMethods，返回 HTTP 200 与 methodResponse，包含 wp.getUsersBlogs 等方法。"},
    {"id": "D-07", "case": "TC-MEDIA-005", "gold": "系统缺陷",
     "log": "上传 0 字节 png，HTTP 500，响应 code=rest_upload_unknown_error，message=File is empty.；同接口正常文件返回 201。"},
    {"id": "D-08", "case": "探索性", "gold": "系统缺陷",
     "log": "未登录访问 /?author=1 返回 301，Location: http://localhost:8080/author/admin/；/?author=2 跳转 /author/editor/。"},
]

merged = existing + new
json.dump(merged, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

from collections import Counter
c = Counter(x["gold"] for x in merged)
print(f"总样本 {len(merged)}：{dict(c)}")
