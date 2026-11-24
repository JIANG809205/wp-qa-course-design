#!/bin/bash
# 正确重建 db 镜像（含 99-qa.cnf）并初始化
set -eu
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
SRC="$APP/local/mariadb"
BUILD=/opt/build/mariadb
COMPOSE="$APP/local/docker-compose.local.yml"

mkdir -p "$BUILD"
cp "$SRC/Dockerfile" "$SRC/entrypoint.sh" "$BUILD/"
echo "--- 构建上下文文件 ---"
ls -l "$BUILD"
grep -c '99-qa.cnf' "$BUILD/Dockerfile" || true

echo
echo "===== 1. 重建镜像 ====="
cd "$BUILD"
timeout 900 docker build -t qa/mariadb:10.6 . 2>&1 | tail -4

echo
echo "===== 2. 验证新镜像内有配置 ====="
docker run --rm qa/mariadb:10.6 bash -c "cat /etc/mysql/mariadb.conf.d/99-qa.cnf" 2>&1 | head -8

echo
echo "===== 3. 重建容器（清卷）====="
cd "$APP/local"
docker compose -f "$COMPOSE" rm -sf db >/dev/null 2>&1 || true
docker volume rm wp-test_db_data >/dev/null 2>&1 || true
docker compose -f "$COMPOSE" up -d db 2>&1 | tail -3
for i in $(seq 1 40); do
  st=$(docker inspect wp-db --format '{{.State.Health.Status}}' 2>/dev/null || echo none)
  [ "$st" = "healthy" ] && break
  sleep 3
done
echo "db health=$st"

echo
echo "===== 4. 监听地址 ====="
docker exec wp-db bash -c "ss -lntp 2>/dev/null | grep 3306 || echo none"

echo
echo "===== 5. 连通性 ====="
docker exec wp-app bash -c 'timeout 3 bash -c "(echo > /dev/tcp/db/3306)" && echo TCP_OK || echo TCP_FAIL'

echo
echo "===== 6. 初始化 WordPress ====="
docker cp "$APP/native/wp-setup.php" wp-app:/tmp/wp-setup.php
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php "http://localhost:8080" "WP-QA-Lab" "admin" "Admin@2026" "admin@example.com" 2>&1 | grep -vE '^\s*$' | tail -16

echo
echo "===== 7. 验证 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
