#!/bin/bash
# 复核三条关键缺陷：登录无锁定 / 0 字节上传 500 / 重复用户名 500
set -u
BASE="http://localhost:8080"
CK=/tmp/wp_ck.txt
rm -f "$CK"

echo "=== DEF-001 连续 6 次错误密码 ==="
for i in 1 2 3 4 5 6; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 10 -c "$CK" -b "$CK" \
    --data-urlencode "log=admin" --data-urlencode "pwd=wrong-pass-$i" \
    --data-urlencode "wp-submit=Log In" --data-urlencode "testcookie=1" \
    "$BASE/wp-login.php")
  echo "  第 $i 次 HTTP=$code"
done
echo "  页面是否出现锁定/验证码提示:"
curl -s -m 10 -b "$CK" "$BASE/wp-login.php" | grep -ciE "验证码|锁定|too many|429" || true

echo
echo "=== DEF-008 0 字节文件上传 ==="
PW=$(cat /tmp/wp_pass/admin.txt 2>/dev/null)
: > /tmp/empty.png
curl -s -o /tmp/up1.json -w '  HTTP=%{http_code}\n' -m 20 \
  -u "admin:$PW" -X POST "$BASE/wp-json/wp/v2/media" \
  -H "Content-Disposition: attachment; filename=empty.png" \
  -H "Content-Type: image/png" --data-binary @/tmp/empty.png
head -c 200 /tmp/up1.json; echo

echo
echo "=== DEF-011 重复用户名 ==="
curl -s -o /tmp/up2.json -w '  HTTP=%{http_code}\n' -m 20 \
  -u "admin:$PW" -X POST "$BASE/wp-json/wp/v2/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Xx123456!","email":"dup@example.com"}'
head -c 200 /tmp/up2.json; echo

echo
echo "=== 版本与数据基线 ==="
docker exec wp-app wp core version --allow-root 2>/dev/null
docker exec wp-app wp post list --post_type=post --format=count --allow-root 2>/dev/null
docker exec wp-app wp comment list --format=count --allow-root 2>/dev/null
docker exec wp-app wp user list --format=count --allow-root 2>/dev/null
