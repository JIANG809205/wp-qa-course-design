#!/bin/bash
# 运行在容器内热启用 Apache 页面缓存 → 预热 → 复压（不重建镜像，10 秒完成）
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 1. 确认容器 ====="
if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
docker ps --format '{{.Names}} {{.Status}}' | head -3
echo "等待站点就绪..."
code=000
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"
[ "$code" != "200" ] && { echo "站点不可用"; exit 1; }

echo
echo "===== 2. 热启用 mod_cache ====="
docker exec wp-app bash -c '
set -e
mkdir -p /var/cache/apache2/mod_cache_disk
chown www-data:www-data /var/cache/apache2/mod_cache_disk
cat > /etc/apache2/conf-available/page-cache.conf <<"CONF"
<IfModule mod_cache.c>
    CacheQuickHandler off
    CacheLock on
    CacheLockPath /tmp/mod_cache-lock
    CacheLockMaxAge 5
    CacheIgnoreHeaders Set-Cookie
    CacheEnable disk "/"
    CacheDisable "/wp-admin"
    CacheDisable "/wp-login.php"
    CacheDisable "/wp-json"
    CacheDefaultExpire 60
    CacheMaxExpire 120
</IfModule>
CacheRoot /var/cache/apache2/mod_cache_disk
CONF
a2enmod cache cache_disk >/dev/null 2>&1
a2enconf page-cache >/dev/null 2>&1
apache2ctl configtest 2>&1 | tail -1
apache2ctl graceful 2>&1 | tail -1
sleep 2
apache2ctl -M 2>/dev/null | grep -E "cache" | head -3
'

echo
echo "===== 3. 预热 ====="
for i in 1 2 3; do curl -s -o /dev/null -w "warm %{http_code} %{time_total}s\n" http://127.0.0.1:8080/; sleep 1; done
docker exec wp-app du -sh /var/cache/apache2/mod_cache_disk 2>/dev/null

echo
echo "===== 4. 复压 100/200 ====="
mkdir -p "$ROOT/results-cache"
for t in 100 200; do
  jtl="/tmp/cache-home-$t.jtl"; rm -f "$jtl"
  printf '  threads=%s ' "$t"
  cd /opt || exit 1
  timeout 400 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t /opt/qa/wp-perf/jmx/perf.jmx -l "$jtl" \
    -Jpath="/" -Jthreads="$t" -Jramp=5 -Jloops=10 >"/tmp/jm-cache-$t.log" 2>&1
  if [ -s "$jtl" ]; then cp "$jtl" "$ROOT/results-cache/home-$t.jtl"; echo "ok samples=$(($(wc -l < "$jtl") - 1))"; else echo FAIL; tail -2 "/tmp/jm-cache-$t.log"; fi
done

echo
echo "===== 5. 对比 ====="
python3 - <<'PY'
import csv, os, statistics

def m(p):
    rows = list(csv.DictReader(open(p, encoding='utf-8', errors='replace')))
    el = sorted(float(r['elapsed']) for r in rows)
    ts = [int(r['timeStamp']) for r in rows]
    dur = max(max(ts)-min(ts), 1)/1000
    return len(rows)/dur, statistics.mean(el), el[int(0.95*len(rows))-1]

base = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results'
cache = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-cache'
print(f"{'并发':<5}{'基线TPS':>8}{'缓存TPS':>9}{'提升':>9}{'基线P95':>8}{'缓存P95':>8}{'降幅':>8}")
for t in (100, 200):
    b = os.path.join(base, f'home-{t}.jtl'); c = os.path.join(cache, f'home-{t}.jtl')
    if not (os.path.exists(b) and os.path.exists(c)):
        print(f"{t}: 缺数据"); continue
    tb, ab, pb = m(b); tc, ac, pc = m(c)
    print(f"{t:<5}{tb:>8.1f}{tc:>9.1f}{(tc-tb)/tb*100:>8.1f}%{pb:>8.0f}{pc:>8.0f}{(pb-pc)/pb*100:>7.1f}%")
PY
