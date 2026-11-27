#!/bin/bash
set -u
echo -n "posts="; docker exec wp-app wp post list --post_type=post --format=count --allow-root
echo -n "pages="; docker exec wp-app wp post list --post_type=page --format=count --allow-root
echo -n "comments="; docker exec wp-app wp comment list --format=count --allow-root
echo -n "users="; docker exec wp-app wp user list --format=count --allow-root
echo -n "roles="; docker exec wp-app wp role list --field=role --allow-root | tr '\n' ' '; echo

PW=$(cat /tmp/wp_pass/admin.txt)
: > /tmp/empty.png
echo "--- multipart 0 字节上传 ---"
curl -s -o /tmp/up3.json -w 'HTTP=%{http_code}\n' -u "admin:$PW" \
  -F 'file=@/tmp/empty.png;type=image/png' http://localhost:8080/wp-json/wp/v2/media
head -c 240 /tmp/up3.json; echo
