#!/bin/bash
# 用官方 zip 离线重建 wordpress 镜像，并保留中文语言包与数据库数据
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
BUILD=/opt/build/wordpress
COMPOSE="$APP/local/docker-compose.local.yml"
ZIP="/mnt/d/迅雷下载/wordpress-7.1.5.zip"

echo "===== 1. 准备构建上下文 ====="
mkdir -p "$BUILD"
cp "$APP/local/wordpress/Dockerfile" "$APP/local/wordpress/init.sh" "$BUILD/"
cp "$ZIP" "$BUILD/wordpress-7.1.5.zip"
ls -lh "$BUILD"

echo
echo "===== 2. 备份中文语言包（web 卷重建后要还回去）====="
rm -rf /tmp/wp-languages
docker cp wp-app:/var/www/html/wp-content/languages /tmp/wp-languages 2>/dev/null \
  && echo "已备份 $(find /tmp/wp-languages -type f | wc -l) 个语言文件" \
  || echo "语言包备份失败（可能不存在）"

echo
echo "===== 3. 构建镜像（官方包，离线）====="
cd "$BUILD" || exit 1
timeout 1800 docker build -t qa/wordpress:7.1.5 . 2>&1 | tail -6

echo
echo "===== 4. 重建容器（清空 web 卷，数据库保留）====="
cd "$APP/local" || exit 1
docker compose -f "$COMPOSE" rm -sf wordpress >/dev/null 2>&1
docker volume rm wp-test_wp_data >/dev/null 2>&1 || echo "  （卷不存在，跳过）"
docker compose -f "$COMPOSE" up -d wordpress 2>&1 | tail -3

code=000
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo
echo "===== 5. 还原中文语言包 ====="
if [ -d /tmp/wp-languages ]; then
  docker cp /tmp/wp-languages wp-app:/var/www/html/wp-content/languages
  docker exec wp-app chown -R www-data:www-data /var/www/html/wp-content/languages
  echo "已还原"
fi
docker exec -u www-data wp-app wp option update WPLANG zh_CN >/dev/null 2>&1
docker exec -u www-data wp-app wp option update blogname 'WP-QA-Lab' >/dev/null 2>&1

echo
echo "===== 6. 验证 ====="
echo "版本: $(docker exec -u www-data wp-app wp core version 2>/dev/null)"
echo "语言: $(docker exec -u www-data wp-app wp language core list --status=active --field=language 2>/dev/null)"
echo "文章: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
echo "用户: $(docker exec -u www-data wp-app wp user list --field=user_login --format=csv 2>/dev/null | tr '\n' ' ')"
echo "首页: $(docker exec -u www-data wp-app wp option get show_on_front 2>/dev/null) / id=$(docker exec -u www-data wp-app wp option get page_on_front 2>/dev/null)"
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1"; do
  printf '  %-40s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
