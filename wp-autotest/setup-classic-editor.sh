#!/bin/bash
# 在容器内安装 mu-plugin：测试环境统一使用经典编辑器，保证选择器稳定
set -u

docker exec wp-app bash -c 'mkdir -p /var/www/html/wp-content/mu-plugins'
docker exec wp-app bash -c 'cat > /var/www/html/wp-content/mu-plugins/qa-classic-editor.php <<"PHP"
<?php
/**
 * Plugin Name: QA Environment Tweaks
 * Description: 课程设计测试环境固定项：关闭区块编辑器，便于自动化定位；关闭编辑器欢迎弹窗。
 */

// 统一使用经典编辑器
add_filter("use_block_editor_for_post_type", "__return_false", 100);
add_filter("use_block_editor_for_post", "__return_false", 100);

// 关闭新用户欢迎弹窗（避免遮挡元素）
remove_action("admin_init", "wp_welcome_panel");

// 首页固定显示固定数量文章，便于脚本定位
add_filter("pre_option_posts_per_page", function () { return 10; });
PHP
chown www-data:www-data /var/www/html/wp-content/mu-plugins/qa-classic-editor.php'

echo "--- 已安装 mu-plugin ---"
docker exec wp-app ls -l /var/www/html/wp-content/mu-plugins/

echo "--- 验证：新建文章页应出现 #title ---"
docker exec wp-app php -r '
require "/var/www/html/wp-load.php";
echo "经典编辑器启用: ", (apply_filters("use_block_editor_for_post_type", true, "post") ? "否" : "是"), PHP_EOL;
'
