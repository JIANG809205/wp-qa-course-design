#!/bin/bash
# 修复容器内 Apache 的 .htaccess 支持与 mod_rewrite
set -u

echo "===== 现状 ====="
docker exec wp-app bash -c "grep -n 'AllowOverride' /etc/apache2/sites-available/000-default.conf || echo '无 AllowOverride 行'"
docker exec wp-app bash -c "apache2ctl -M 2>/dev/null | grep -i rewrite || echo 'rewrite 未加载'"
docker exec wp-app bash -c "ls -l /var/www/html/.htaccess; head -3 /var/www/html/.htaccess"

echo
echo "===== 修复：加全局 Directory 配置并加载 rewrite ====="
docker exec wp-app bash -c '
  printf "%s\n" "<Directory /var/www/html>" "    Options Indexes FollowSymLinks" "    AllowOverride All" "    Require all granted" "</Directory>" > /etc/apache2/conf-available/wp-qa.conf
  a2enconf wp-qa >/dev/null 2>&1
  a2enmod rewrite >/dev/null 2>&1
  apache2ctl configtest 2>&1 | tail -1
  apache2ctl graceful 2>&1 | tail -2
'
sleep 3

echo
echo "===== 复测 ====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
echo "--- REST 返回片段 ---"
curl -s "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=1" | head -c 200
echo
