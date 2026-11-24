#!/bin/bash
# 执行 JMeter 压测矩阵：4 场景 × 3 并发级别
# 结果写入 wp-perf/results/*.jtl（CSV 格式）
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
WORK=/opt/qa/wp-perf
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 0. 准备 ====="
code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/ || echo 000)
echo "站点 HTTP=$code"
[ "$code" != "200" ] && { echo "站点不可用"; exit 1; }

# 取一个文章 ID 用于详情页场景
PID=$(curl -s "http://127.0.0.1:8080/wp-json/wp/v2/posts?per_page=1" | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['id'])" 2>/dev/null)
echo "详情页文章 ID=$PID"

rm -rf "$WORK"; mkdir -p "$WORK/jmx" "$WORK/results"
cp "$ROOT/jmx/"*.jmx "$WORK/jmx/"
mkdir -p "$ROOT/results"

run() {
  name="$1"; plan="$2"; path="$3"; threads="$4"; loops="$5"
  jtl="$WORK/results/${name}.jtl"
  printf '  %-24s threads=%-4s ' "$name" "$threads"
  cd "$WORK" || exit 1
  timeout 600 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t "$WORK/jmx/$plan" -l "$jtl" \
    -Jpath="$path" -Jthreads="$threads" -Jramp=5 -Jloops="$loops" \
    >"/tmp/jm-$name.log" 2>&1
  if [ -s "$jtl" ]; then
    lines=$(($(wc -l < "$jtl") - 1))
    err=$(awk -F',' 'NR>1 && $8=="false"' "$jtl" | wc -l)
    echo "samples=$lines errors=$err"
  else
    echo "FAILED"
    tail -3 "/tmp/jm-$name.log"
  fi
}

echo
echo "===== 1. 首页 ====="
for t in 10 50 100 200; do
  run "home-$t" perf.jmx "/" "$t" 10
done

echo
echo "===== 2. 文章详情 ====="
for t in 10 50 100; do
  run "detail-$t" perf.jmx "/?p=$PID" "$t" 10
done

echo
echo "===== 3. 搜索 ====="
for t in 10 50 100; do
  run "search-$t" perf.jmx "/?s=test" "$t" 10
done

echo
echo "===== 4. 后台文章列表（含登录）====="
for t in 10 50; do
  run "admin-$t" perf-admin.jmx "/wp-admin/edit.php" "$t" 5
done

echo
echo "===== 5. 回传 ====="
cp -f "$WORK/results/"*.jtl "$ROOT/results"/ 2>/dev/null
ls -lh "$ROOT/results" | tail -15
