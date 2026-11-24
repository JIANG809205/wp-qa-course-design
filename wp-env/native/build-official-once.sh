#!/bin/bash
# 一次调用内完成：起 dockerd → 用官方 zip 构建 → 重建容器 → 还原中文包 → 验证
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
BUILD=/opt/build/wordpress
COMPOSE="$APP/local/docker-compose.local.yml"

echo "===== 1. dockerd ====="
if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 20); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
echo "ok $(docker info --format '{{.ServerVersion}}' 2>&1)"

echo
echo "===== 2. 备份语言包 ====="
rm -rf /tmp/wp-languages
docker cp wp-app:/var/www/html/wp-content/languages /tmp/wp-languages 2>/dev/null \
  && echo "备份 $(find /tmp/wp-languages -type f | wc -l) 个文件" || echo "无语言包"

echo
echo "===== 3. 构建（官方 zip，离线）====="
mkdir -p "$BUILD"
cp "$APP/local/wordpress/Dockerfile" "$APP/local/wordpress/init.sh" "$BUILD/"
cp "/mnt/d/迅雷下载/wordpress-7.1.5.zip" "$BUILD/wordpress-7.1.5.zip"
cd "$BUILD" || exit 1
timeout 900 docker build -q -t qa/wordpress:7.1.5 . >/tmp/build-off.log 2>&1
rc=$?
echo "build rc=$rc"
if [ $rc -ne 0 ]; then echo "构建失败，保留原镜像"; tail -5 /tmp/build-off.log; exit 1; fi
docker image inspect qa/wordpress:7.1.5 --format '新镜像: {{.Created}}'

echo
echo "===== 4. 重建容器（数据库保留）====="
cd "$APP/local" || exit 1
docker compose -f "$COMPOSE" rm -sf wordpress >/dev/null 2>&1
docker volume rm wp-test_wp_data >/dev/null 2>&1 || true
docker compose -f "$COMPOSE" up -d wordpress 2>&1 | tail -2
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 2
done
echo "HTTP=$code"

echo
echo "===== 5. 还原语言包 ====="
if [ -d /tmp/wp-languages ]; then
  docker cp /tmp/wp-languages wp-app:/var/www/html/wp-content/languages 2>/dev/null
  docker exec wp-app chown -R www-data:www-data /var/www/html/wp-content/languages 2>/dev/null
fi
docker exec -u www-data wp-app wp option update WPLANG zh_CN >/dev/null 2>&1

echo
echo "===== 6. 验证 ====="
echo "版本: $(docker exec -u www-data wp-app wp core version 2>/dev/null)"
echo "文章: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
echo "用户: $(docker exec -u www-data wp-app wp user list --field=user_login --format=csv 2>/dev/null | tr '\n' ' ')"
echo "首页: $(docker exec -u www-data wp-app wp option get show_on_front 2>/dev/null) id=$(docker exec -u www-data wp-app wp option get page_on_front 2>/dev/null)"
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1"; do
  printf '  %-40s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' -L "http://127.0.0.1:8080$u")"
done
