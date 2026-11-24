#!/bin/bash
# 优化实验：启用 WordPress Redis 对象缓存 → 复压首页 → 对比
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
WORK=/opt/qa/wp-perf
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 1. 下载 redis-cache 插件 ====="
if curl -fsSL -m 180 -o /tmp/redis-cache.zip https://downloads.wordpress.org/plugin/redis-cache.zip; then
  echo "下载成功 $(du -h /tmp/redis-cache.zip | cut -f1)"
else
  echo "下载失败"; exit 1
fi

echo
echo "===== 2. 安装并启用对象缓存 ====="
docker cp /tmp/redis-cache.zip wp-app:/tmp/redis-cache.zip
docker exec wp-app bash -c 'cd /var/www/html/wp-content/plugins && unzip -oq /tmp/redis-cache.zip && ls -d redis-cache*'
docker exec wp-app bash -c 'cp /var/www/html/wp-content/plugins/redis-cache/includes/object-cache.php /var/www/html/wp-content/object-cache.php && chown www-data:www-data /var/www/html/wp-content/object-cache.php && echo dropin_installed'

echo "--- 验证缓存读写 ---"
docker exec wp-app php -r '
require "/var/www/html/wp-load.php";
wp_cache_set("qa_probe", "ok", "qa", 120);
echo "cache_get = ", wp_cache_get("qa_probe", "qa"), PHP_EOL;
echo "external object cache = ", (wp_using_ext_object_cache() ? "是" : "否"), PHP_EOL;
'
echo "--- Redis 中的 key 数量 ---"
docker exec wp-redis redis-cli dbsize 2>/dev/null

echo
echo "===== 3. 复压首页（10/50/100/200）====="
mkdir -p "$ROOT/results-opt"
for t in 10 50 100 200; do
  jtl="/tmp/opt-home-$t.jtl"
  rm -f "$jtl"
  printf '  home-opt-%s threads=%s ' "$t" "$t"
  cd /opt || exit 1
  timeout 600 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t "$WORK/jmx/perf.jmx" -l "$jtl" \
    -Jpath="/" -Jthreads="$t" -Jramp=5 -Jloops=10 >"/tmp/jm-opt-$t.log" 2>&1
  if [ -s "$jtl" ]; then
    cp "$jtl" "$ROOT/results-opt/home-$t.jtl"
    echo "samples=$(($(wc -l < "$jtl") - 1))"
  else
    echo "FAILED"; tail -3 "/tmp/jm-opt-$t.log"
  fi
done

echo
echo "===== 4. 对比 ====="
python3 - <<'PY'
import csv, glob, os, statistics

def m(path):
    rows = list(csv.DictReader(open(path, encoding='utf-8', errors='replace')))
    el = sorted(float(r['elapsed']) for r in rows)
    ts = [int(r['timeStamp']) for r in rows]
    dur = max(max(ts)-min(ts), 1)/1000
    n = len(rows)
    err = sum(1 for r in rows if str(r['success']).lower() != 'true')
    return n, n/dur, statistics.mean(el), el[int(0.95*n)-1], err*100/n

base = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results'
opt = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-opt'
print(f"{'并发':<6}{'基线TPS':>9}{'优化TPS':>9}{'提升':>8}{'基线P95':>9}{'优化P95':>9}{'降幅':>8}")
for t in (10, 50, 100, 200):
    b = os.path.join(base, f'home-{t}.jtl')
    o = os.path.join(opt, f'home-{t}.jtl')
    if not (os.path.exists(b) and os.path.exists(o)):
        continue
    nb, tb, ab, p95b, eb = m(b)
    no, to, ao, p95o, eo = m(o)
    print(f"{t:<6}{tb:>9.1f}{to:>9.1f}{(to-tb)/tb*100:>7.1f}%{p95b:>9.0f}{p95o:>9.0f}{(p95b-p95o)/p95b*100:>7.1f}%")
PY
