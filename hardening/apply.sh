#!/bin/bash
# 应用加固：mu-plugin + Apache 配置，并重启 Apache
set -u
DIR="/mnt/e/软件质量保证与测试课程设计/hardening"
docker cp "$DIR/qa-hardening.php" wp-app:/var/www/html/wp-content/mu-plugins/qa-hardening.php
docker cp "$DIR/qa-hardening.conf" wp-app:/etc/apache2/conf-available/qa-hardening.conf
docker exec wp-app php -l /var/www/html/wp-content/mu-plugins/qa-hardening.php
docker exec wp-app a2enconf qa-hardening 2>&1 | tail -2
docker exec wp-app apache2ctl graceful 2>&1 | tail -2
sleep 2
echo "--- 加固后自检 ---"
curl -s -o /dev/null -w '首页 HTTP=%{http_code}\n' -L http://localhost:8080/
curl -s -o /dev/null -w '后台 HTTP=%{http_code}\n' http://localhost:8080/wp-login.php
