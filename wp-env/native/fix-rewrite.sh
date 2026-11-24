#!/bin/bash
# 写入 WordPress 标准的 .htaccess 重写规则（CLI 下 flush 不会自动生成）
set -u
WP=/var/www/html

cat > "${WP}/.htaccess" <<'EOF'
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
EOF

chown www-data:www-data "${WP}/.htaccess"
chmod 644 "${WP}/.htaccess"

echo "--- mod_rewrite ---"
apache2ctl -M 2>/dev/null | grep -i rewrite || echo "rewrite NOT enabled"

echo "--- 重启 Apache ---"
service apache2 stop >/dev/null 2>&1
sleep 1
service apache2 start
sleep 2

echo "--- 自检 ---"
curl -s -o /dev/null -w "home     http=%{http_code}\n" "http://127.0.0.1:8080/"
curl -s -o /dev/null -w "rest     http=%{http_code}\n" "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=2"
curl -s -o /dev/null -w "login    http=%{http_code}\n" "http://127.0.0.1:8080/wp-login.php"
curl -s "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=1" | head -c 200
echo
