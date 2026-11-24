#!/bin/bash
# 解释"静态首页比列表页慢"：比较响应体积、单请求耗时、模板与查询
set -u
B="http://localhost:8080"

echo "===== 1. 响应体积与单请求耗时（各 5 次）====="
for path in "/" "/?page_id=1054"; do
  printf '%-18s ' "$path"
  for i in 1 2 3 4 5; do
    curl -s -o /dev/null -w '%{size_download}B/%{time_total}s  ' "$B$path"
  done
  echo
done

echo
echo "===== 2. 页面 HTML 体积 ====="
echo "首页   : $(curl -s "$B/" | wc -c) 字节"
echo "列表页 : $(curl -s "$B/?page_id=1054" | wc -c) 字节"

echo
echo "===== 3. 各自使用的模板 ====="
docker exec -u www-data wp-app wp eval '
$home = (int) get_option("page_on_front");
$blog = (int) get_option("page_for_posts");
echo "page_on_front=$home  page_for_posts=$blog\n";
echo "首页模板: " . get_page_template_slug($home) . " (空=默认 page 模板)\n";
echo "首页区块数: " . count(parse_blocks(get_post($home)->post_content)) . "\n";
echo "列表页每页文章数: " . get_option("posts_per_page") . "\n";
'

echo
echo "===== 4. 单页查询次数（SAVEQUERIES）====="
docker exec -u www-data wp-app wp eval '
define("SAVEQUERIES", true);
global $wpdb;
foreach (["/" => "首页", "/?page_id=1054" => "列表页"] as $u => $name) {
  $wpdb->queries = [];
  $html = wp_remote_get("http://127.0.0.1:8080" . $u)["body"] ?? "";
  echo "$name: 由外部请求，查询数需在目标进程统计（跳过）\n";
}
' 2>&1 | tail -3
