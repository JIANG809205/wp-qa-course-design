#!/bin/bash
# 为 admin 创建应用密码（供接口自动化使用），并验证权限
set -u
WP="docker exec -u www-data wp-app wp"

echo "===== 1. 现有应用密码 ====="
$WP user application-password list admin --fields=uuid,name,created --format=table 2>/dev/null || echo "（无）"

echo
echo "===== 2. 创建 ci-admin 应用密码 ====="
PW=$($WP user application-password create admin ci-admin --porcelain 2>/dev/null)
if [ -n "$PW" ]; then
  echo "已创建，长度 ${#PW}"
  printf '%s' "$PW" > /tmp/admin_app_pass.txt
else
  echo "创建失败（可能已存在），尝试列出后重建"
  $WP user application-password list admin --field=uuid --format=csv 2>/dev/null | while read -r u; do
    [ -n "$u" ] && $WP user application-password delete admin "$u" >/dev/null 2>&1
  done
  PW=$($WP user application-password create admin ci-admin --porcelain 2>/dev/null)
  printf '%s' "$PW" > /tmp/admin_app_pass.txt
  echo "重建完成，长度 ${#PW}"
fi

echo
echo "===== 3. 验证接口鉴权 ====="
BASE=http://127.0.0.1:8080
CODE=$(curl -s -o /tmp/me.json -w '%{http_code}' -m 20 -u "admin:$(cat /tmp/admin_app_pass.txt)" "$BASE/wp-json/wp/v2/users/me")
echo "GET /users/me -> HTTP $CODE"
python3 -c "
import json
d=json.load(open('/tmp/me.json'))
print('  用户:', d.get('name'), '角色:', d.get('roles'))
" 2>/dev/null || head -c 200 /tmp/me.json

echo
echo "===== 4. 验证可写权限（建草稿后删除）====="
CODE=$(curl -s -o /tmp/newpost.json -w '%{http_code}' -m 25 -u "admin:$(cat /tmp/admin_app_pass.txt)" \
  -H 'Content-Type: application/json' \
  -d '{"title":"api-probe","status":"draft","content":"probe"}' \
  "$BASE/wp-json/wp/v2/posts")
echo "POST /posts -> HTTP $CODE"
PID=$(python3 -c "import json;print(json.load(open('/tmp/newpost.json')).get('id',''))" 2>/dev/null)
echo "  新文章 ID: $PID"
if [ -n "$PID" ]; then
  curl -s -o /dev/null -w '  删除 -> HTTP %{http_code}\n' -m 20 -X DELETE -u "admin:$(cat /tmp/admin_app_pass.txt)" "$BASE/wp-json/wp/v2/posts/$PID?force=true"
fi

echo
echo "===== 5. WP-CLI 版本与官方数据构造能力 ====="
$WP core version
$WP post list --post_type=post --post_status=publish --format=count
