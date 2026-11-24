#!/bin/bash
# WordPress 容器入口：按环境变量生成 wp-config.php，等待数据库，启动 Apache
set -e

: "${WORDPRESS_DB_HOST:=db:3306}"
: "${WORDPRESS_DB_NAME:=wordpress}"
: "${WORDPRESS_DB_USER:=wpuser}"
: "${WORDPRESS_DB_PASSWORD:=wp_pass_2026}"
: "${WORDPRESS_TABLE_PREFIX:=wp_}"

DB_HOST="${WORDPRESS_DB_HOST%%:*}"

if [ ! -f /var/www/html/wp-config.php ]; then
  echo "[init] 生成 wp-config.php"
  SALTS=$(php -r '
    $keys = ["AUTH_KEY","SECURE_AUTH_KEY","LOGGED_IN_KEY","NONCE_KEY","AUTH_SALT","SECURE_AUTH_SALT","LOGGED_IN_SALT","NONCE_SALT"];
    foreach ($keys as $k) { echo "define(\x27$k\x27, \x27" . bin2hex(random_bytes(20)) . "\x27);\n"; }
  ')
  cat > /var/www/html/wp-config.php <<PHPEOF
<?php
define('DB_NAME', '${WORDPRESS_DB_NAME}');
define('DB_USER', '${WORDPRESS_DB_USER}');
define('DB_PASSWORD', '${WORDPRESS_DB_PASSWORD}');
define('DB_HOST', '${WORDPRESS_DB_HOST}');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');
${SALTS}
\$table_prefix = '${WORDPRESS_TABLE_PREFIX}';
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
define('WP_ENVIRONMENT_TYPE', 'local');
define('WP_POST_REVISIONS', 5);
define('WP_REDIS_HOST', 'redis');
define('WP_REDIS_PORT', 6379);
if (!defined('ABSPATH')) { define('ABSPATH', __DIR__ . '/'); }
require_once ABSPATH . 'wp-settings.php';
PHPEOF
fi

chown -R www-data:www-data /var/www/html

echo "[wait] 等待数据库 ${DB_HOST}:3306"
for i in $(seq 1 60); do
  if (echo > /dev/tcp/"${DB_HOST}"/3306) >/dev/null 2>&1; then
    echo "[wait] 数据库可达"
    break
  fi
  sleep 2
done

echo "[start] Apache 启动"
exec apache2ctl -D FOREGROUND
