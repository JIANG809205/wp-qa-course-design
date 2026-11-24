#!/bin/bash
# 起一个"干净安装"的 WordPress 实例（8081），用于对照"正常部署"的样子
set -u
NET=wp-test_default
IMG=qa/wordpress:7.1.5

echo "===== 1. 环境检查 ====="
if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
docker ps --format '{{.Names}} {{.Status}}' | head -5

echo
echo "===== 2. 建独立数据库 ====="
docker exec wp-db mariadb -e "
CREATE DATABASE IF NOT EXISTS wp_clean DEFAULT CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON wp_clean.* TO 'wpuser'@'%';
FLUSH PRIVILEGES;" 2>&1

echo
echo "===== 3. 启动干净实例（8081）====="
docker rm -f wp-clean >/dev/null 2>&1
docker run -d --name wp-clean --network $NET \
  -e WORDPRESS_DB_HOST=db:3306 -e WORDPRESS_DB_NAME=wp_clean \
  -e WORDPRESS_DB_USER=wpuser -e WORDPRESS_DB_PASSWORD=wp_pass_2026 \
  -p 8081:8080 "$IMG" >/dev/null 2>&1 && echo "容器已启动"

for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8081/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 3
done
echo "8081 HTTP=$code"

echo
echo "===== 4. 执行标准安装（wp-cli）====="
docker exec wp-clean mkdir -p /tmp/wpc 2>/dev/null
docker cp /tmp/wp-cli.phar wp-clean:/usr/local/bin/wp 2>/dev/null
docker exec wp-clean chmod +x /usr/local/bin/wp
docker exec -u www-data wp-clean wp core is-installed 2>/dev/null && echo "已安装" || \
  docker exec -u www-data wp-clean wp core install \
    --url=http://localhost:8081 --title="WordPress 干净实例" \
    --admin_user=admin --admin_password='Admin@2026' --admin_email=admin@example.com --skip-email 2>&1 | tail -3

echo
echo "===== 5. 干净实例的内容（应为默认 Hello World + 示例页面）====="
docker exec -u www-data wp-clean wp post list --post_type=post --fields=ID,post_title,post_status --format=csv 2>&1
docker exec -u www-data wp-clean wp post list --post_type=page --fields=ID,post_title --format=csv 2>&1
echo "主题: $(docker exec -u www-data wp-clean wp theme list --status=active --field=name 2>/dev/null)"
echo "插件数: $(docker exec -u www-data wp-clean wp plugin list --format=count 2>/dev/null)"

echo
echo "===== 6. 主实例与干净实例对照 ====="
echo "主实例(8080) 文章数: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
echo "干净实例(8081) 文章数: $(docker exec -u www-data wp-clean wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
