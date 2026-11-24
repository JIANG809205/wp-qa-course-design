#!/bin/bash
# 页面缓存优化实验：重建镜像 → 预热 → 复压 100/200 → 三方对比
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
BUILD=/opt/build
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 1. dockerd ====="
if docker info >/dev/null 2>&1; then echo running; else
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
  echo "started $(docker info --format '{{.ServerVersion}}' 2>&1)"
fi

echo
echo "===== 2. 重建 wordpress 镜像（加 mod_cache）====="
mkdir -p "$BUILD/wordpress"
cp "$APP/local/wordpress/Dockerfile" "$APP/local/wordpress/init.sh" "$BUILD/wordpress/"
timeout 1200 docker build -q -t qa/wordpress:7.1.5 "$BUILD/wordpress" >/tmp/b3.log 2>&1 \
  && echo "构建 OK" || { echo "构建失败"; tail -5 /tmp/b3.log; exit 1; }

echo
echo "===== 3. 重建容器 ====="
cd "$APP/local" || exit 1
docker compose -f docker-compose.local.yml up -d --force-recreate wordpress 2>&1 | tail -3
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo
echo "===== 4. 预热缓存 ====="
for i in 1 2 3; do curl -s -o /dev/null http://127.0.0.1:8080/; sleep 1; done
docker exec wp-app bash -c 'ls /var/cache/apache2/mod_cache_disk 2>/dev/null | head -3; du -sh /var/cache/apache2/mod_cache_disk 2>/dev/null'

echo
echo "===== 5. 复压 100/200 ====="
mkdir -p "$ROOT/results-cache"
for t in 100 200; do
  jtl="/tmp/cache-home-$t.jtl"; rm -f "$jtl"
  printf '  threads=%s ' "$t"
  cd /opt || exit 1
  timeout 600 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t /opt/qa/wp-perf/jmx/perf.jmx -l "$jtl" \
    -Jpath="/" -Jthreads="$t" -Jramp=5 -Jloops=10 >"/tmp/jm-cache-$t.log" 2>&1
  if [ -s "$jtl" ]; then cp "$jtl" "$ROOT/results-cache/home-$t.jtl"; echo "ok samples=$(($(wc -l < "$jtl") - 1))"; else echo FAIL; tail -2 "/tmp/jm-cache-$t.log"; fi
done

echo
echo "===== 6. 三方对比 ====="
python3 - <<'PY'
import csv, os, statistics

def m(p):
    rows = list(csv.DictReader(open(p, encoding='utf-8', errors='replace')))
    el = sorted(float(r['elapsed']) for r in rows)
    ts = [int(r['timeStamp']) for r in rows]
    dur = max(max(ts)-min(ts), 1)/1000
    n = len(rows)
    return n/dur, statistics.mean(el), el[int(0.95*n)-1]

base = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results'
tuned = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-tuned'
cache = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-cache'

print(f"{'并发':<5}{'基线TPS':>8}{'参数调优':>9}{'页面缓存':>9}{'缓存提升':>9}{'基线P95':>8}{'缓存P95':>8}")
for t in (100, 200):
    b = os.path.join(base, f'home-{t}.jtl')
    v = os.path.join(tuned, f'home-{t}.jtl')
    c = os.path.join(cache, f'home-{t}.jtl')
    tb, ab, pb = m(b) if os.path.exists(b) else (0, 0, 0)
    tv, av, pv = m(v) if os.path.exists(v) else (0, 0, 0)
    tc, ac, pc = m(c) if os.path.exists(c) else (0, 0, 0)
    gain = (tc - tb) / tb * 100 if tb else 0
    print(f"{t:<5}{tb:>8.1f}{tv:>9.1f}{tc:>9.1f}{gain:>8.1f}%{pb:>8.0f}{pc:>8.0f}")
PY
