#!/bin/bash
# 原生 LAMP 方式部署 WordPress 测试环境（适配无 systemd / 无 bridge 的 WSL）
# 用法：wsl -d Ubuntu-22.04 -u root -- bash /mnt/e/.../wp-env/native/native-setup.sh
set -u
export DEBIAN_FRONTEND=noninteractive

DB_NAME=${DB_NAME:-wordpress}
DB_USER=${DB_USER:-wpuser}
DB_PASS=${DB_PASS:-wp_pass_2026}
SITE_URL=${SITE_URL:-http://localhost:8080}
SITE_TITLE=${SITE_TITLE:-WP-QA-Lab}
ADMIN_USER=${ADMIN_USER:-admin}
ADMIN_PASS=${ADMIN_PASS:-Admin@2026}
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
WP_DIR=/var/www/html

echo "==> [1/8] 启动 MariaDB"
mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
service mariadb status >/dev/null 2>&1 || service mariadb start
for i in $(seq 1 20); do
  mariadb-admin ping >/dev/null 2>&1 && break
  sleep 1
done

echo "==> [2/8] 创建数据库与账号"
mariadb <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
echo "    ok"

echo "==> [3/8] 下载 WordPress"
if [ ! -f /tmp/wordpress.tar.gz ]; then
  if ! wget -q -T 120 -O /tmp/wordpress.tar.gz https://cn.wordpress.org/latest-zh_CN.tar.gz; then
    echo "    cn 镜像失败，改用官方源"
    wget -q -T 180 -O /tmp/wordpress.tar.gz https://wordpress.org/latest.tar.gz
  fi
fi
ls -lh /tmp/wordpress.tar.gz

echo "==> [4/8] 解压到 ${WP_DIR}"
if [ ! -f "${WP_DIR}/wp-settings.php" ]; then
  rm -rf /tmp/wordpress
  tar xzf /tmp/wordpress.tar.gz -C /tmp
  rm -f "${WP_DIR}/index.html"
  cp -a /tmp/wordpress/. "${WP_DIR}/"
  echo "    已解压"
else
  echo "    已存在，跳过"
fi

echo "==> [5/8] 生成 wp-config.php"
if [ ! -f "${WP_DIR}/wp-config.php" ]; then
  SALTS=$(php -r '
    $k = ["AUTH_KEY","SECURE_AUTH_KEY","LOGGED_IN_KEY","NONCE_KEY","AUTH_SALT","SECURE_AUTH_SALT","LOGGED_IN_SALT","NONCE_SALT"];
    foreach ($k as $x) { echo "define(\x27$x\x27, \x27" . bin2hex(random_bytes(24)) . "\x27);\n"; }
  ')
  cat > "${WP_DIR}/wp-config.php" <<PHPEOF
<?php
define('DB_NAME', '${DB_NAME}');
define('DB_USER', '${DB_USER}');
define('DB_PASSWORD', '${DB_PASS}');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');
${SALTS}
\$table_prefix = 'wp_';
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
define('WP_POST_REVISIONS', 5);
define('WP_REDIS_HOST', '127.0.0.1');
define('WP_REDIS_PORT', 6379);
if (!defined('ABSPATH')) { define('ABSPATH', __DIR__ . '/'); }
require_once ABSPATH . 'wp-settings.php';
PHPEOF
  echo "    已生成"
else
  echo "    已存在，跳过"
fi

echo "==> [6/8] 配置 Apache（端口 8080 + 允许 .htaccess）"
sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/ports.conf
sed -i 's/<VirtualHost \*:80>/<VirtualHost *:8080>/' /etc/apache2/sites-available/000-default.conf
if ! grep -q 'AllowOverride All' /etc/apache2/sites-available/000-default.conf; then
  sed -i 's|AllowOverride None|AllowOverride All|' /etc/apache2/sites-available/000-default.conf
fi
a2enmod rewrite >/dev/null 2>&1
php -m | grep -q mysqli || echo "    !! mysqli 未加载"
service apache2 status >/dev/null 2>&1 || service apache2 start
sleep 2

echo "==> [7/8] 目录权限"
chown -R www-data:www-data "${WP_DIR}"
find "${WP_DIR}" -type d -exec chmod 755 {} \;
find "${WP_DIR}" -type f -exec chmod 644 {} \;

echo "==> [8/8] 安装 WordPress 并造数据"
php /mnt/e/软件质量保证与测试课程设计/wp-env/native/wp-setup.php \
  "${SITE_URL}" "${SITE_TITLE}" "${ADMIN_USER}" "${ADMIN_PASS}" "${ADMIN_EMAIL}"

echo "----- 自检 -----"
curl -s -o /dev/null -w "front http=%{http_code}\n" "${SITE_URL}/"
curl -s -o /dev/null -w "admin http=%{http_code}\n" "${SITE_URL}/wp-admin/"
php -r 'echo "php ok\n";'
