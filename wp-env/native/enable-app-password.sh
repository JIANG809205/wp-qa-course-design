#!/bin/bash
# 应用密码在 http://localhost 下需要 WP_ENVIRONMENT_TYPE=local 才可用
set -u
WP=/var/www/html
if grep -q "WP_ENVIRONMENT_TYPE" "$WP/wp-config.php"; then
  echo "already set"
else
  sed -i "/define('WP_DEBUG', true);/a define('WP_ENVIRONMENT_TYPE', 'local');" "$WP/wp-config.php"
  echo "added"
fi
grep -n "WP_ENVIRONMENT_TYPE\|WP_DEBUG\|WP_REDIS" "$WP/wp-config.php"
