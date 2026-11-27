#!/bin/bash
# 查看测试残留：文章、评论、用户
set -u
echo "=== 疑似测试文章 ==="
docker exec -u www-data wp-app wp post list --post_type=post --post_status=any \
  --fields=ID,post_title,post_status --format=csv 2>/dev/null | grep -Ei "perm|try-edit|qa-" | head -10
echo "=== 全部文章数（按状态）==="
docker exec wp-db mariadb -N -e "SELECT post_status, COUNT(*) FROM wordpress.wp_posts WHERE post_type='post' GROUP BY post_status;"
echo "=== 疑似测试评论 ==="
docker exec wp-db mariadb -N -e "SELECT comment_ID, LEFT(comment_content,30), comment_approved FROM wordpress.wp_comments WHERE comment_content LIKE 'qa%' OR comment_content LIKE '%自动化%' LIMIT 10;"
echo "=== 用户列表 ==="
docker exec -u www-data wp-app wp user list --fields=ID,user_login,roles --format=csv 2>/dev/null
