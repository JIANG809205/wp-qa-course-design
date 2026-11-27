#!/bin/bash
# 用 SQL 清理测试残留（快），并清理 term 关系
set -u
Q() { docker exec wp-db mariadb -N -e "$1"; }

echo "===== 清理前 ====="
Q "SELECT CONCAT('文章:', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';"
Q "SELECT CONCAT('评论:', COUNT(*)) FROM wordpress.wp_comments;"
Q "SELECT CONCAT('用户:', COUNT(*)) FROM wordpress.wp_users;"

echo
echo "===== 删除测试文章（perm-*/try-edit/qa-*）====="
Q "DELETE pm FROM wordpress.wp_postmeta pm
   JOIN wordpress.wp_posts p ON p.ID = pm.post_id
   WHERE p.post_type='post' AND (p.post_title LIKE 'perm-%' OR p.post_title='try-edit' OR p.post_title LIKE 'qa-%');"
Q "DELETE tr FROM wordpress.wp_term_relationships tr
   JOIN wordpress.wp_posts p ON p.ID = tr.object_id
   WHERE p.post_type='post' AND (p.post_title LIKE 'perm-%' OR p.post_title='try-edit' OR p.post_title LIKE 'qa-%');"
Q "DELETE FROM wordpress.wp_posts
   WHERE post_type='post' AND (post_title LIKE 'perm-%' OR post_title='try-edit' OR post_title LIKE 'qa-%');"
Q "SELECT ROW_COUNT() AS deleted_posts;"

echo
echo "===== 删除测试评论 ====="
Q "DELETE FROM wordpress.wp_comments
   WHERE comment_content LIKE 'qa%'
      OR comment_content LIKE '%自动化评论%'
      OR comment_content LIKE '%自动化XSS测试%';"
Q "SELECT ROW_COUNT() AS deleted_comments;"

echo
echo "===== 删除测试用户 ====="
Q "DELETE um FROM wordpress.wp_usermeta um JOIN wordpress.wp_users u ON u.ID=um.user_id
   WHERE u.user_login LIKE 'perm%' OR u.user_login='dup_probe' OR u.user_login LIKE 'qa\_%';"
Q "DELETE FROM wordpress.wp_users
   WHERE user_login LIKE 'perm%' OR user_login='dup_probe' OR user_login LIKE 'qa\_%';"
Q "SELECT ROW_COUNT() AS deleted_users;"

echo
echo "===== 清理后 ====="
Q "SELECT CONCAT('文章:', COUNT(*)) FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish';"
Q "SELECT CONCAT('评论:', COUNT(*)) FROM wordpress.wp_comments;"
Q "SELECT CONCAT('用户:', COUNT(*)) FROM wordpress.wp_users;"
echo "站点: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/)"
