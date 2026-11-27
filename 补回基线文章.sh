#!/bin/bash
# 补回被误删的 1 篇文章，使基线恢复为 1000 篇
set -u
WP="docker exec -u www-data wp-app wp"
Q() { docker exec wp-db mariadb -N -e "$1"; }

echo "=== 编号范围 ==="
Q "SELECT MIN(CAST(SUBSTRING_INDEX(post_title,'：',1) AS CHAR)) FROM wordpress.wp_posts WHERE post_title LIKE '测试文章%' LIMIT 1;"
Q "SELECT post_title FROM wordpress.wp_posts WHERE post_title LIKE '测试文章%' ORDER BY ID DESC LIMIT 3;"

echo
echo "=== 是否已有 1000 号 ==="
exists=$($WP post list --post_type=post --post_status=publish --format=ids -- 2>/dev/null | head -0; \
  docker exec wp-db mariadb -N -e "SELECT COUNT(*) FROM wordpress.wp_posts WHERE post_title='测试文章 1000：质量保证与测试实践';")
echo "1000 号存在数: $exists"

if [ "${exists:-0}" -eq 0 ]; then
  id=$($WP post create --post_type=post --post_status=publish --post_title='测试文章 1000：质量保证与测试实践' \
       --post_content='这是第 1000 篇用于性能与分页测试的文章。关键词：软件测试、质量保证、自动化。' \
       --porcelain 2>/dev/null)
  echo "已补建 #$id"
fi

echo
echo "=== 恢复后 ==="
Q "SELECT CONCAT('文章:', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';"
Q "SELECT CONCAT('评论:', COUNT(*)) FROM wordpress.wp_comments;"
Q "SELECT CONCAT('用户:', COUNT(*)) FROM wordpress.wp_users;"
