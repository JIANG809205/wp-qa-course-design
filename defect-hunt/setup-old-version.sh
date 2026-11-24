#!/bin/bash
# 起一个 WordPress 7.1.4 实例（8082），用于双版本对照
set -u
BUILD=/opt/build/wp1714
ZIPURL="https://wordpress.org/wordpress-7.1.4.tar.gz"

if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 25); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi

echo "===== 1. 下载 7.1.4 官方包 ====="
mkdir -p "$BUILD"
if [ ! -s "$BUILD/wordpress-7.1.4.tar.gz" ]; then
  curl -fsSL -m 300 -o "$BUILD/wordpress-7.1.4.tar.gz" "$ZIPURL" \
    && echo "下载完成 $(du -h $BUILD/wordpress-7.1.4.tar.gz | cut -f1)" \
    || { echo "下载失败"; exit 1; }
fi
rm -rf "$BUILD/wordpress"
tar xzf "$BUILD/wordpress-7.1.4.tar.gz" -C "$BUILD"
grep "wp_version =" "$BUILD/wordpress/wp-includes/version.php"

echo
echo "===== 2. 构建 7.1.4 镜像 ====="
cat > "$BUILD/Dockerfile" <<'EOF'
FROM qa/wordpress:7.1.5
USER root
RUN rm -rf /var/www/html/* /var/www/html/.[!.]* 2>/dev/null || true
COPY wordpress/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html
EOF
cd "$BUILD" || exit 1
timeout 600 docker build -q -t qa/wordpress:7.1.4 . 2>&1 | tail -3

echo
echo "===== 3. 建库并启动容器（8082）====="
docker exec wp-db mariadb -e "
CREATE DATABASE IF NOT EXISTS wp_old DEFAULT CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON wp_old.* TO 'wpuser'@'%';
FLUSH PRIVILEGES;" 2>&1

docker rm -f wp-old >/dev/null 2>&1
docker run -d --name wp-old --network wp-test_default \
  -e WORDPRESS_DB_HOST=db:3306 -e WORDPRESS_DB_NAME=wp_old \
  -e WORDPRESS_DB_USER=wpuser -e WORDPRESS_DB_PASSWORD=wp_pass_2026 \
  -p 8082:8080 qa/wordpress:7.1.4 >/dev/null && echo "容器已启动"

code=000
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8082/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 3
done
echo "8082 HTTP=$code"

echo
echo "===== 4. 安装 7.1.4 ====="
docker cp /tmp/wp-cli.phar wp-old:/usr/local/bin/wp 2>/dev/null || true
docker exec wp-old chmod +x /usr/local/bin/wp 2>/dev/null
docker exec -u www-data wp-old wp core install \
  --url=http://localhost:8082 --title="QA-OLD-714" \
  --admin_user=admin --admin_password='Admin@2026' --admin_email=old@example.com --skip-email 2>&1 | tail -2
docker exec -u www-data wp-old wp core version 2>/dev/null
