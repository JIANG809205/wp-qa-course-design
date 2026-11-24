#!/bin/bash
# 归一化 7.1.4 环境：固定链接、调试日志、测试数据，使两版本可比
set -u
OLD="docker exec -u www-data wp-old wp"

echo "===== 1. 设置固定链接（否则 /wp-json/ 全部 404）====="
$OLD rewrite structure '/%postname%/' --hard 2>&1 | tail -1
$OLD rewrite flush --hard 2>&1 | tail -1
echo "permalink: $($OLD option get permalink_structure 2>/dev/null)"

echo
echo "===== 2. 生成 debug.log（触发一次 PHP 警告，使 P02 可测）====="
$OLD eval 'trigger_error("qa-probe: simulated warning", E_USER_WARNING);' 2>&1 | tail -1
$OLD config get WP_DEBUG_LOG 2>/dev/null

echo
echo "===== 3. 与 7.1.5 对齐测试数据（文章 20 篇）====="
n=$($OLD post list --post_type=post --post_status=publish --format=count 2>/dev/null)
echo "当前文章数: $n"
if [ "${n:-0}" -lt 20 ]; then
  $OLD post generate --count=20 --post_type=post --post_status=publish --post_author=1 >/dev/null 2>&1
  echo "生成后: $($OLD post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
fi

echo
echo "===== 4. 复核关键端点 ====="
for p in "/" "/wp-json/wp/v2/users" "/?author=1" "/wp-content/debug.log"; do
  printf '%-30s ' "$p"
  curl -s -o /dev/null -m 10 -w 'HTTP %{http_code} -> %{redirect_url}\n' "http://localhost:8082$p"
done

echo
echo "===== 5. 插件/主题是否一致 ====="
echo "7.1.5 插件: $(docker exec -u www-data wp-app wp plugin list --field=name --format=csv 2>/dev/null | tr '\n' ' ')"
echo "7.1.4 插件: $($OLD plugin list --field=name --format=csv 2>/dev/null | tr '\n' ' ')"
echo "7.1.5 主题: $(docker exec -u www-data wp-app wp theme list --status=active --field=name 2>/dev/null)"
echo "7.1.4 主题: $($OLD theme list --status=active --field=name 2>/dev/null)"
