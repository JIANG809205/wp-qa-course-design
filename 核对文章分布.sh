#!/bin/bash
# 核对文章标题分布，定位被多删的那篇
set -u
Q() { docker exec wp-db mariadb -N -e "$1"; }
echo "=== 各状态文章数 ==="
Q "SELECT post_status, COUNT(*) FROM wordpress.wp_posts WHERE post_type='post' GROUP BY post_status;"
echo "=== 标题前缀分布 ==="
Q "SELECT SUBSTRING_INDEX(post_title, ' ', 1) AS prefix, COUNT(*) FROM wordpress.wp_posts
   WHERE post_type='post' AND post_status='publish' GROUP BY prefix ORDER BY COUNT(*) DESC LIMIT 5;"
echo "=== 编号连续性检查（测试文章 N）==="
Q "SELECT MIN(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(post_title,'篇',1),'第',-1) AS UNSIGNED)) AS min_no,
         MAX(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(post_title,'篇',1),'第',-1) AS UNSIGNED)) AS max_no,
         COUNT(*) AS cnt
   FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish' AND post_title LIKE '%第%篇%';"
echo "=== 不含编号的已发布文章 ==="
Q "SELECT ID, post_title FROM wordpress.wp_posts WHERE post_type='post' AND post_status='publish'
   AND post_title NOT LIKE '%第%篇%' LIMIT 10;"
