#!/bin/bash
# 复核清理结果；探测 WP-CLI 的可用下载源
set -u

echo "===== 1. 清理结果复核（直接 SQL，避开对象缓存）====="
docker exec wp-db mariadb -N -e "
SELECT CONCAT('publish 文章: ', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';
SELECT CONCAT('残留 perm 文章: ', COUNT(*)) FROM wordpress.wp_posts WHERE post_title LIKE 'perm-%';
SELECT CONCAT('残留测试用户: ', COUNT(*)) FROM wordpress.wp_users WHERE user_login LIKE 'perm%' OR user_login='dup_probe';
SELECT CONCAT('站点标题: ', option_value) FROM wordpress.wp_options WHERE option_name='blogname';
"

echo
echo "===== 2. 探测 WP-CLI 下载源 ====="
probe() {
  printf '%-70s ' "$1"
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -L "$1" 2>/dev/null)
  echo "HTTP $code"
}
probe "https://cdn.jsdelivr.net/gh/wp-cli/builds@gh-pages/phar/wp-cli.phar"
probe "https://fastly.jsdelivr.net/gh/wp-cli/builds@gh-pages/phar/wp-cli.phar"
probe "https://packagist.org/"
probe "https://mirrors.aliyun.com/composer/"
probe "https://gitee.com/"
