#!/bin/bash
# 重建带性能调优的镜像 → 复压首页 100/200 → 与基线对比
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
BUILD=/opt/build
WORK=/opt/qa/wp-perf
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 1. 同步并重建镜像 ====="
mkdir -p "$BUILD/mariadb" "$BUILD/wordpress"
cp "$APP/local/mariadb/Dockerfile" "$APP/local/mariadb/entrypoint.sh" "$BUILD/mariadb/"
cp "$APP/local/wordpress/Dockerfile" "$APP/local/wordpress/init.sh" "$BUILD/wordpress/"
timeout 900 docker build -q -t qa/mariadb:10.6 "$BUILD/mariadb" >/tmp/b1.log 2>&1 && echo "db 镜像 OK" || { echo "db 构建失败"; tail -3 /tmp/b1.log; }
timeout 1200 docker build -q -t qa/wordpress:7.1.5 "$BUILD/wordpress" >/tmp/b2.log 2>&1 && echo "wp 镜像 OK" || { echo "wp 构建失败"; tail -3 /tmp/b2.log; }

echo
echo "===== 2. 重建容器 ====="
cd "$APP/local" || exit 1
docker compose -f docker-compose.local.yml up -d --force-recreate 2>&1 | tail -4
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo "--- 生效参数 ---"
docker exec wp-app bash -c "grep -E 'MaxRequestWorkers|ServerLimit' /etc/apache2/mods-enabled/mpm_prefork.conf"
docker exec wp-db mariadb -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';" 2>/dev/null | tail -1

echo
echo "===== 3. 复压 100/200 ====="
mkdir -p "$ROOT/results-tuned"
for t in 100 200; do
  jtl="/tmp/tuned-home-$t.jtl"; rm -f "$jtl"
  printf '  tuned-%s ' "$t"
  cd /opt || exit 1
  timeout 600 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t "$WORK/jmx/perf.jmx" -l "$jtl" \
    -Jpath="/" -Jthreads="$t" -Jramp=5 -Jloops=10 >"/tmp/jm-tuned-$t.log" 2>&1
  if [ -s "$jtl" ]; then cp "$jtl" "$ROOT/results-tuned/home-$t.jtl"; echo "samples=$(($(wc -l < "$jtl") - 1))"; else echo FAIL; fi
done

echo
echo "===== 4. 对比 ====="
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
print(f"{'并发':<6}{'基线TPS':>9}{'调优TPS':>9}{'提升':>8}{'基线P95':>9}{'调优P95':>9}")
for t in (100, 200):
    b = os.path.join(base, f'home-{t}.jtl'); v = os.path.join(tuned, f'home-{t}.jtl')
    if not (os.path.exists(b) and os.path.exists(v)): continue
    tb, ab, p95b = m(b); tv, av, p95v = m(v)
    print(f"{t:<6}{tb:>9.1f}{tv:>9.1f}{(tv-tb)/tb*100:>7.1f}%{p95b:>9.0f}{p95v:>9.0f}")
PY
