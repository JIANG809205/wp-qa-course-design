#!/bin/bash
# 一键启动 Docker 栈：dockerd + compose + 初始化 + 保活
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
COMPOSE="$APP/local/docker-compose.local.yml"

echo "===== 1. dockerd ====="
if docker info >/dev/null 2>&1; then
  echo "already running: $(docker info --format '{{.ServerVersion}}')"
else
  pkill -9 dockerd 2>/dev/null
  sleep 2
  rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
  echo "started: $(docker info --format '{{.ServerVersion}}' 2>&1)"
fi

echo
echo "===== 2. 保活进程（钉住 WSL 虚拟机）====="
if ! pgrep -f dsh-wp-keepalive >/dev/null 2>&1; then
  setsid nohup bash -c 'exec -a dsh-wp-keepalive sleep infinity' >/dev/null 2>&1 &
  sleep 1
fi
pgrep -af dsh-wp-keepalive | head -1

echo
echo "===== 3. compose up ====="
cd "$APP/local" || exit 1
docker compose -f "$COMPOSE" up -d 2>&1 | tail -6
sleep 8
docker compose -f "$COMPOSE" ps

echo
echo "===== 4. 等待站点 ====="
code=000
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo
echo "===== 5. 初始化数据 ====="
docker cp "$APP/native/wp-setup.php" wp-app:/tmp/wp-setup.php
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php "http://localhost:8080" "WP-QA-Lab" "admin" "Admin@2026" "admin@example.com" 2>&1 | tail -22

echo
echo "===== 6. .htaccess ====="
docker exec wp-app bash -c 'printf "%s\n" "# BEGIN WordPress" "<IfModule mod_rewrite.c>" "RewriteEngine On" "RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]" "RewriteBase /" "RewriteRule ^index\.php\$ - [L]" "RewriteCond %{REQUEST_FILENAME} !-f" "RewriteCond %{REQUEST_FILENAME} !-d" "RewriteRule . /index.php [L]" "</IfModule>" "# END WordPress" > /var/www/html/.htaccess; chown www-data:www-data /var/www/html/.htaccess; echo written'

echo
echo "===== 7. 验证 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
echo "--- 数据 ---"
docker exec wp-app php -r 'define("WP_USE_THEMES",false); require "/var/www/html/wp-load.php"; global $wpdb; printf("WP %s | 文章 %s | 评论 %s | 用户 %s\n", get_bloginfo("version"), wp_count_posts("post")->publish, $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"), count_users()["total_users"]);' 2>&1 | tail -2
