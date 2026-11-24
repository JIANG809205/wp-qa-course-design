#!/bin/bash
# 重建 MariaDB 镜像并重启栈，然后重新初始化 WordPress
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
COMPOSE="$APP/local/docker-compose.local.yml"
BUILD=/opt/build

echo "===== 1. 同步 entrypoint 并重建 qa/mariadb ====="
cp "$APP/mariadb/entrypoint.sh" "$BUILD/mariadb/" 2>/dev/null || {
  mkdir -p "$BUILD/mariadb"
  cp "$APP/mariadb/Dockerfile" "$APP/mariadb/entrypoint.sh" "$BUILD/mariadb/"
}
cd "$BUILD/mariadb" || exit 1
timeout 900 docker build -t qa/mariadb:10.6 . 2>&1 | tail -3
echo "rc=${PIPESTATUS[0]}"

echo
echo "===== 2. 重启栈（数据卷保留）====="
cd "$APP/local" || exit 1
docker compose -f "$COMPOSE" up -d --force-recreate db 2>&1 | tail -4
sleep 12
docker compose -f "$COMPOSE" ps

echo
echo "===== 3. 网络连通性检查 ====="
docker exec wp-app bash -c '(echo > /dev/tcp/db/3306) 2>/dev/null && echo "db:3306 可达" || echo "db:3306 不可达"'

echo
echo "===== 4. 重新初始化 ====="
docker cp "$APP/native/wp-setup.php" wp-app:/tmp/wp-setup.php
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php "http://localhost:8080" "WP-QA-Lab" "admin" "Admin@2026" "admin@example.com" 2>&1 | grep -vE '^\s*$' | tail -18

echo
echo "===== 5. 验证 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
