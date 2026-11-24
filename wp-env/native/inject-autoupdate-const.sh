#!/bin/bash
# 用 sed 把 AUTOMATIC_UPDATER_DISABLED 常量写进 wp-config.php（容器内无 python3）
set -u
docker exec wp-app bash -c '
  f=/var/www/html/wp-config.php
  if grep -q AUTOMATIC_UPDATER_DISABLED "$f"; then
    echo "already present"
  else
    cp "$f" "$f.bak"
    sed -i "s|^/\* That.s all, stop editing|\
define(\"AUTOMATIC_UPDATER_DISABLED\", true);\n\n&|" "$f"
    grep -q AUTOMATIC_UPDATER_DISABLED "$f" && echo "injected" || echo "inject failed"
  fi
'
echo "--- 复核 ---"
docker exec wp-app grep -n "AUTOMATIC_UPDATER_DISABLED" /var/www/html/wp-config.php || echo "未找到常量"
docker exec -u www-data wp-app wp core version
curl -s -o /dev/null -w "站点 HTTP %{http_code}\n" http://localhost:8080/
