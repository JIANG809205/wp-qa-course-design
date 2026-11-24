#!/bin/bash
# 重建 db 镜像（幂等建库版）→ 重启 → 初始化 WordPress
set -eu
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
SRC="$APP/local/mariadb"
BUILD=/opt/build/mariadb
COMPOSE="$APP/local/docker-compose.local.yml"

mkdir -p "$BUILD"
cp "$SRC/Dockerfile" "$SRC/entrypoint.sh" "$BUILD/"

echo "===== 1. 重建镜像 ====="
cd "$BUILD"
timeout 900 docker build -t qa/mariadb:10.6 . 2>&1 | tail -3

echo
echo "===== 2. 重建 db 容器 ====="
cd "$APP/local"
docker compose -f "$COMPOSE" rm -sf db >/dev/null 2>&1 || true
docker compose -f "$COMPOSE" up -d db 2>&1 | tail -2
for i in $(seq 1 40); do
  st=$(docker inspect wp-db --format '{{.State.Health.Status}}' 2>/dev/null || echo none)
  [ "$st" = "healthy" ] && break
  sleep 3
done
echo "health=$st"

echo
echo "===== 3. 账号是否创建 ====="
sleep 3
docker exec wp-db mariadb -e "SHOW DATABASES; SELECT User,Host FROM mysql.user WHERE User='wpuser';" 2>&1 | head -12

echo
echo "===== 4. app 侧连接测试 ====="
docker exec wp-app php -r '$c=@mysqli_connect("db","wpuser","wp_pass_2026","wordpress",3306); echo $c ? "MYSQL_OK\n" : "MYSQL_FAIL: ".mysqli_connect_error()."\n";' 2>&1

echo
echo "===== 5. 初始化 WordPress ====="
docker cp "$APP/native/wp-setup.php" wp-app:/tmp/wp-setup.php
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php "http://localhost:8080" "WP-QA-Lab" "admin" "Admin@2026" "admin@example.com" 2>&1 | grep -vE '^\s*$' | tail -16

echo
echo "===== 6. 验证 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
docker exec wp-app bash -c 'printf "%s\n" "# BEGIN WordPress" "<IfModule mod_rewrite.c>" "RewriteEngine On" "RewriteBase /" "RewriteRule ^index\.php$ - [L]" "RewriteCond %{REQUEST_FILENAME} !-f" "RewriteCond %{REQUEST_FILENAME} !-d" "RewriteRule . /index.php [L]" "</IfModule>" "# END WordPress" > /var/www/html/.htaccess; chown www-data:www-data /var/www/html/.htaccess'
echo "htaccess written"
curl -s -o /dev/null -w "rest after htaccess: %{http_code}\n" "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=1"
