#!/bin/bash
# 用 WP-CLI 定位并修复首页异常文章（标题被改成 try-edit / 正文为 x 的测试残留）
set -u
WP="docker exec -u www-data wp-app wp"

echo "===== 1. 当前异常记录 ====="
$WP db query "SELECT ID, post_title, post_name, LEFT(post_content,30) AS content
              FROM wp_posts
              WHERE post_type='post' AND post_status='publish'
                AND (post_title LIKE '%try-edit%' OR post_content='x')
              ORDER BY ID;" 2>&1

echo
echo "===== 2. 正文为 x 的测试文章：直接删除 ====="
for id in $($WP db query "SELECT ID FROM wp_posts WHERE post_type='post' AND post_content='x';" --skip-column-names 2>/dev/null); do
  $WP post delete "$id" --force >/dev/null 2>&1 && echo "  已删除 #$id"
done

echo
echo "===== 3. 标题被改的文章：按正文编号还原 ====="
for id in $($WP db query "SELECT ID FROM wp_posts WHERE post_type='post' AND post_content LIKE '%这是第%篇%' AND post_title LIKE '%try-edit%';" --skip-column-names 2>/dev/null); do
  num=$($WP post get "$id" --field=post_content 2>/dev/null | grep -oE '第[0-9]+篇' | grep -oE '[0-9]+' | head -1)
  if [ -n "$num" ]; then
    $WP post update "$id" --post_title="测试文章 ${num}：质量保证与测试实践" --post_name="test-post-${num}" >/dev/null 2>&1
    echo "  还原 #$id -> 测试文章 ${num}"
  else
    $WP post update "$id" --post_title="测试文章：质量保证与测试实践" --post_name="test-post-$id" >/dev/null 2>&1
    echo "  还原 #$id（无编号）"
  fi
done

echo
echo "===== 4. 复核 ====="
$WP db query "SELECT COUNT(*) AS try_edit FROM wp_posts WHERE post_type='post' AND post_title LIKE '%try-edit%';" 2>&1
$WP db query "SELECT COUNT(*) AS content_x FROM wp_posts WHERE post_type='post' AND post_content='x';" 2>&1
echo "publish: $($WP post list --post_type=post --post_status=publish --format=count)"
echo "首页前 3 篇:"
$WP post list --post_type=post --post_status=publish --fields=ID,post_title --format=csv 2>/dev/null | head -4
