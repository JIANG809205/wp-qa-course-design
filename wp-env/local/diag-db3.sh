#!/bin/bash
# 检查 db 内用户/库，以及 app 侧连接失败的具体原因
echo "===== db 内数据库与用户 ====="
docker exec wp-db mariadb -e "SHOW DATABASES; SELECT User,Host FROM mysql.user;" 2>&1

echo
echo "===== 容器环境变量 ====="
docker exec wp-db env | grep -i mariadb
echo "--- app ---"
docker exec wp-app env | grep -i wordpress

echo
echo "===== wp-config.php 关键行 ====="
docker exec wp-app grep -E "DB_NAME|DB_USER|DB_HOST|DB_PASSWORD|table_prefix" /var/www/html/wp-config.php

echo
echo "===== app 侧用 CLI 直连测试 ====="
docker exec wp-app php -r '$c=@mysqli_connect("db","wpuser","wp_pass_2026","wordpress",3306); if($c){echo "MYSQL_OK\n";}else{echo "MYSQL_FAIL: ".mysqli_connect_error()."\n";}' 2>&1

echo
echo "===== db 日志 ====="
docker logs --tail 20 wp-db 2>&1 | tail -20
