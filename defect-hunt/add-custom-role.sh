#!/bin/bash
# 1) 创建自定义角色"审核员"并建用户；2) 检查 Firefox/geckodriver 可用性
set -u
W="docker exec -u www-data wp-app wp"

echo "===== 1. 创建自定义角色 auditor ====="
$W eval '
$caps = [
  "read" => true,
  "edit_posts" => true,
  "moderate_comments" => true,   // 可审核评论
  "upload_files" => false,       // 不能上传
  "publish_posts" => false,      // 不能发布
  "edit_others_posts" => false,
  "manage_options" => false,
];
remove_role("auditor");
add_role("auditor", "审核员", $caps);
$r = get_role("auditor");
echo "角色已建: " . ($r ? "OK" : "FAIL") . "\n";
echo "权限: " . implode(", ", array_keys(array_filter($r->capabilities))) . "\n";
' 2>&1 | tail -4

echo
echo "===== 2. 创建 auditor 用户 ====="
$W user get auditor --field=ID >/dev/null 2>&1 || $W user create auditor auditor@example.com --role=auditor --user_pass='Auditor@2026' 2>&1 | tail -1
$W user list --role=auditor --fields=user_login,roles --format=table 2>&1 | tail -2

echo
echo "===== 3. 跨浏览器可行性 ====="
printf '%-42s ' "apt: firefox-geckodriver"
apt-cache policy firefox-geckodriver 2>/dev/null | head -2 | tr '\n' ' '; echo
printf '%-42s ' "apt: firefox-esr"
apt-cache policy firefox-esr 2>/dev/null | head -2 | tr '\n' ' '; echo
printf '%-42s ' "download.mozilla.org"
curl -s -o /dev/null -m 20 -w '%{http_code}\n' -L "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=zh-CN"
printf '%-42s ' "geckodriver (github)"
curl -s -o /dev/null -m 15 -w '%{http_code}\n' -L "https://github.com/mozilla/geckodriver/releases/latest"
