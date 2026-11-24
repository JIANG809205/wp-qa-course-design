#!/bin/bash
# 取博客页/首页的规范 URL，并验证响应体积
set -u
docker exec -u www-data wp-app wp eval '
echo "blog  permalink: " . get_permalink(1054) . "\n";
echo "home  permalink: " . get_permalink(1053) . "\n";
echo "home  option   : " . home_url("/") . "\n";
' 2>&1 | tail -4

echo "--- 候选 URL 验证 ---"
for u in "/" "/qa-blog/" "/blog/" "/?page_id=1054"; do
  printf '%-18s ' "$u"
  curl -s -o /dev/null -m 10 -w 'HTTP %{http_code}  %{size_download}B  %{time_total}s  redirect=%{redirect_url}\n' \
    "http://localhost:8080$u"
done
