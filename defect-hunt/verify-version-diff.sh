#!/bin/bash
# 核实 P06/P07/P08/P09 在两个版本上的真实差异，排除"数据/配置差异"造成的假阳性
set -u
NEW=http://localhost:8080
OLD=http://localhost:8082

echo "===== P07 REST 用户列表 ====="
for base in "$NEW" "$OLD"; do
  printf '%-24s ' "$base/wp-json/wp/v2/users"
  curl -s -m 10 "$base/wp-json/wp/v2/users" | head -c 200; echo
done

echo
echo "===== P06 作者枚举（?author=1）====="
for base in "$NEW" "$OLD"; do
  printf '%-24s ' "$base"
  curl -s -o /dev/null -m 10 -w 'HTTP %{http_code} -> %{redirect_url}\n' "$base/?author=1"
done

echo
echo "===== 数据量对比（作者归档是否存在取决于文章数）====="
echo "7.1.5 文章数: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"
echo "7.1.4 文章数: $(docker exec -u www-data wp-old wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"

echo
echo "===== debug.log 是否存在（取决于是否发生过错误）====="
for base in "$NEW" "$OLD"; do
  printf '%-24s ' "$base/wp-content/debug.log"
  curl -s -o /dev/null -m 10 -w 'HTTP %{http_code}\n' "$base/wp-content/debug.log"
done
echo "7.1.4 配置: $(docker exec -u www-data wp-old wp config get WP_DEBUG_LOG 2>/dev/null || echo '未设置')"
echo "7.1.5 配置: $(docker exec -u www-data wp-app wp config get WP_DEBUG_LOG 2>/dev/null || echo '未设置')"
