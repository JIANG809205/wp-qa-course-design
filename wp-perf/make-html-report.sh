#!/bin/bash
# 生成 JMeter HTML 报告（在 ASCII 路径下执行，避免 Java 中文路径异常）
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
cd /opt || exit 1

for n in home-200 admin-50 home-100; do
  src="$ROOT/results/$n.jtl"
  [ -f "$src" ] || { echo "$n 缺少 jtl"; continue; }
  cp "$src" "/tmp/$n.jtl"
  out="/tmp/jmrep-$n"
  rm -rf "$out"
  java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar \
    -g "/tmp/$n.jtl" -o "$out" >"/tmp/jmrep-$n.log" 2>&1
  if [ -f "$out/index.html" ]; then
    rm -rf "$ROOT/report-$n"
    cp -r "$out" "$ROOT/report-$n"
    echo "OK  $n -> report-$n/index.html  ($(du -sh "$out" | cut -f1))"
  else
    echo "FAIL $n"; tail -3 "/tmp/jmrep-$n.log"
  fi
done
