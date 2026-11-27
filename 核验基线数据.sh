#!/bin/bash
# 核对基线数据与 debug.log 实际大小
set -u
echo "=== debug.log ==="
docker exec wp-app sh -c 'ls -l /var/www/html/wp-content/debug.log 2>/dev/null || echo "不存在"'
echo "=== 数据库基线 ==="
docker exec wp-db mariadb -N -e "
SELECT CONCAT('文章: ', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';
SELECT CONCAT('评论: ', COUNT(*)) FROM wordpress.wp_comments;
SELECT CONCAT('用户: ', COUNT(*)) FROM wordpress.wp_users;
"
echo "=== 版本 ==="
docker exec -u www-data wp-app wp core version 2>/dev/null
