#!/bin/bash
# 关闭 WordPress 自动更新（站点选项 + wp-config 常量），并验证版本未漂移
set -u
W="docker exec -u www-data wp-app wp"

echo "===== 1. 关闭四个自动更新开关 ====="
$W option update auto_update_core_major disabled 2>&1 | tail -1
$W option update auto_update_core_minor disabled 2>&1 | tail -1
$W option update auto_update_plugins disabled 2>&1 | tail -1
$W option update auto_update_themes disabled 2>&1 | tail -1

echo
echo "===== 2. 写入常量到 wp-config.php ====="
docker exec wp-app bash -c '
  f=/var/www/html/wp-config.php
  if ! grep -q AUTOMATIC_UPDATER_DISABLED "$f"; then
    python3 - "$f" <<PY
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
mark = "/* That\x27s all, stop editing!"
add = "define(\"AUTOMATIC_UPDATER_DISABLED\", true);\n\n"
if mark in s:
    s = s.replace(mark, add + mark, 1)
else:
    s = s.rstrip() + "\n" + add
open(p, "w", encoding="utf-8").write(s)
print("constant injected")
PY
  else
    echo "constant already present"
  fi
'
docker exec wp-app grep -n "AUTOMATIC_UPDATER_DISABLED" /var/www/html/wp-config.php || echo "未写入"

echo
echo "===== 3. 复核 ====="
for k in auto_update_core_major auto_update_core_minor auto_update_plugins auto_update_themes; do
  printf '%-26s ' "$k"
  $W option get "$k" 2>/dev/null || echo "(空)"
done
echo "版本: $($W core version 2>/dev/null)"
echo "站点: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/)"
