#!/bin/bash
# 把 mu-plugin 安装进容器（幂等）
set -u
docker exec wp-app bash -c 'mkdir -p /var/www/html/wp-content/mu-plugins'
docker cp "/mnt/e/软件质量保证与测试课程设计/wp-autotest/qa-mu-plugin.php" \
  wp-app:/var/www/html/wp-content/mu-plugins/qa-tweaks.php
docker exec wp-app bash -c 'chown -R www-data:www-data /var/www/html/wp-content/mu-plugins'
echo "--- mu-plugins ---"
docker exec wp-app ls -l /var/www/html/wp-content/mu-plugins/
echo "--- 校验 ---"
docker exec wp-app php -r 'require "/var/www/html/wp-load.php"; echo "经典编辑器: ", apply_filters("use_block_editor_for_post_type", true, "post") ? "否" : "是", PHP_EOL;'
