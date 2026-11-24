#!/bin/bash
# 只补列表页 100 并发的 3 次（其余两档已完成）
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar
OUT="$ROOT/results-rigor-blog"
mkdir -p "$OUT"

for rep in 1 2 3; do
  jtl="/tmp/blog-100-$rep.jtl"
  rm -f "$jtl"
  cd /opt || exit 1
  timeout 240 java -Djmeter.home=/opt/apache-jmeter-5.6.3 -jar "$JM" -n \
    -t /opt/qa/wp-perf/jmx/perf-duration.jmx -l "$jtl" \
    -Jpath="/qa-blog/" -Jthreads=100 -Jramp=10 -Jduration=60 \
    >"/tmp/blog-100-$rep.log" 2>&1
  [ -s "$jtl" ] && cp "$jtl" "$OUT/blog-100-rep$rep.jtl" && echo "rep$rep 完成"
done
echo "文件数: $(ls "$OUT"/*.jtl 2>/dev/null | wc -l)"
