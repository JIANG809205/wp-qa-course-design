#!/bin/bash
# 检查 PHP 配置，并生成 JMeter HTML 报告
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"

echo "===== 1. PHP / OPcache 现状 ====="
docker exec wp-app php -v | head -2
docker exec wp-app php -i 2>/dev/null | grep -E "^opcache.enable|^opcache.memory_consumption|^Loaded Configuration" | head -5
docker exec wp-app php -m 2>/dev/null | grep -i opcache || echo "OPcache 未安装"

echo
echo "===== 2. Apache MPM 与并发上限 ====="
docker exec wp-app bash -c "apache2ctl -M 2>/dev/null | grep -i mpm"
docker exec wp-app bash -c "grep -E 'MaxRequestWorkers|StartServers|ServerLimit' /etc/apache2/mods-enabled/mpm_*.conf 2>/dev/null || echo '默认配置'"

echo
echo "===== 3. 数据库连接上限 ====="
docker exec wp-db mariadb -e "SHOW VARIABLES LIKE 'max_connections';" 2>/dev/null

echo
echo "===== 4. 生成 JMeter HTML 报告 ====="
for n in home-200 admin-50; do
  out="/tmp/jmreport-$n"
  rm -rf "$out"
  java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar \
    -g "$ROOT/results/$n.jtl" -o "$out" >/tmp/jmrep-$n.log 2>&1
  if [ -f "$out/index.html" ]; then
    mkdir -p "$ROOT/report-$n"
    cp -r "$out"/. "$ROOT/report-$n"/
    echo "  $n -> report-$n/index.html"
  else
    echo "  $n 生成失败"; tail -3 /tmp/jmrep-$n.log
  fi
done
ls "$ROOT" | head
