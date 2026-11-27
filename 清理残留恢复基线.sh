#!/bin/bash
# 清理测试残留，恢复基线：1000 篇已发布文章 / 20000 条评论 / 6 个角色账号
set -u
WP="docker exec -u www-data wp-app wp"

echo "===== 清理前 ====="
docker exec wp-db mariadb -N -e "
SELECT CONCAT('文章:', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';
SELECT CONCAT('评论:', COUNT(*)) FROM wordpress.wp_comments;
SELECT CONCAT('用户:', COUNT(*)) FROM wordpress.wp_users;"

echo
echo "===== 删除测试文章 ====="
for id in $($WP post list --post_type=post --post_status=any --format=ids 2>/dev/null); do
  title=$($WP post get "$id" --field=post_title 2>/dev/null || echo "")
  case "$title" in
    perm-*|try-edit|qa-*) $WP post delete "$id" --force >/dev/null 2>&1 && echo "  删除 #$id ($title)" ;;
  esac
done

echo
echo "===== 删除测试评论 ====="
docker exec wp-db mariadb -e "
DELETE FROM wordpress.wp_comments
WHERE comment_content LIKE 'qa%'
   OR comment_content LIKE '%自动化评论%'
   OR comment_content LIKE '%自动化XSS测试%';" 2>&1 | tail -2

echo
echo "===== 删除测试用户 ====="
for u in $($WP user list --field=user_login --format=csv 2>/dev/null); do
  case "$u" in
    perm*|dup_probe|qa_*) $WP user delete "$u" --yes >/dev/null 2>&1 && echo "  删除用户 $u" ;;
  esac
done

echo
echo "===== 清理后 ====="
docker exec wp-db mariadb -N -e "
SELECT CONCAT('文章:', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';
SELECT CONCAT('评论:', COUNT(*)) FROM wordpress.wp_comments;
SELECT CONCAT('用户:', COUNT(*)) FROM wordpress.wp_users;"
echo "站点: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/)"
echo "版本: $($WP core version 2>/dev/null)"
