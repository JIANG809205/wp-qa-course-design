#!/bin/bash
# 启动 Docker 版 WordPress 环境并初始化数据
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
COMPOSE="$APP/local/docker-compose.local.yml"
cd "$APP/local" || exit 1

echo "===== 1. 停掉原生 LAMP（释放 8080）====="
service apache2 stop >/dev/null 2>&1
service mariadb stop >/dev/null 2>&1
service redis-server stop >/dev/null 2>&1
pkill -f dsh-keepalive 2>/dev/null
echo "done"

echo
echo "===== 2. 启动容器栈 ====="
docker compose -f "$COMPOSE" up -d 2>&1 | tail -8
sleep 8
docker compose -f "$COMPOSE" ps

echo
echo "===== 3. 等待站点就绪 ====="
code=000
for i in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/ 2>/dev/null)
  if [ "$code" != "000" ]; then break; fi
  sleep 3
done
echo "首页 HTTP=$code （302/200 均表示 Apache 已起）"

echo
echo "===== 4. 初始化 WordPress 数据 ====="
docker cp "$APP/native/wp-setup.php" wp-app:/tmp/wp-setup.php 2>&1
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php "http://localhost:8080" "WP-QA-Lab" "admin" "Admin@2026" "admin@example.com" 2>&1 | tail -25

echo
echo "===== 5. 写入 .htaccess（固定链接）====="
docker exec wp-app bash -c 'cat > /var/www/html/.htaccess <<EOF
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
EOF
chown www-data:www-data /var/www/html/.htaccess'
echo "done"

echo
echo "===== 6. 验证 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-40s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
curl -s "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=1" | head -c 160
echo
