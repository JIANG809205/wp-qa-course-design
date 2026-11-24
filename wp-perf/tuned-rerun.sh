#!/bin/bash
# 单次调用完成：起 dockerd → 重建容器（应用调优镜像）→ 复压 100/200 → 对比
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar

echo "===== 1. 启动 dockerd ====="
if docker info >/dev/null 2>&1; then
  echo "running"
else
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
  echo "started: $(docker info --format '{{.ServerVersion}}' 2>&1)"
fi

echo
echo "===== 2. 重建容器（应用调优镜像）====="
cd "$APP/local" || exit 1
docker compose -f docker-compose.local.yml up -d --force-recreate 2>&1 | tail -5
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo
echo "===== 3. 确认调优参数生效 ====="
docker exec wp-app bash -c "grep -E 'MaxRequestWorkers|ServerLimit' /etc/apache2/mods-enabled/mpm_prefork.conf" 2>&1
docker exec wp-app php -i 2>/dev/null | grep -E '^opcache.memory_consumption' | head -1
docker exec wp-db mariadb -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';" 2>/dev/null | tail -1

echo
echo "===== 4. 复压首页 100/200 ====="
mkdir -p "$ROOT/results-tuned"
for t in 100 200; do
  jtl="/tmp/tuned-home-$t.jtl"; rm -f "$jtl"
  printf '  threads=%s ' "$t"
  cd /opt || exit 1
  timeout 600 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
    -jar "$JM" -n -t /opt/qa/wp-perf/jmx/perf.jmx -l "$jtl" \
    -Jpath="/" -Jthreads="$t" -Jramp=5 -Jloops=10 >"/tmp/jm-tuned-$t.log" 2>&1
  if [ -s "$jtl" ]; then cp "$jtl" "$ROOT/results-tuned/home-$t.jtl"; echo "ok samples=$(($(wc -l < "$jtl") - 1))"; else echo FAIL; tail -2 "/tmp/jm-tuned-$t.log"; fi
done

echo
echo "===== 5. 对比（基线 vs 调优）====="
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
print(f"{'并发':<6}{'基线TPS':>9}{'调优TPS':>9}{'TPS提升':>9}{'基线P95':>9}{'调优P95':>9}{'P95降幅':>9}")
for t in (100, 200):
    b = os.path.join(base, f'home-{t}.jtl'); v = os.path.join(tuned, f'home-{t}.jtl')
    if not (os.path.exists(b) and os.path.exists(v)):
        print(f"{t}: 缺少数据"); continue
    tb, ab, p95b = m(b); tv, av, p95v = m(v)
    print(f"{t:<6}{tb:>9.1f}{tv:>9.1f}{(tv-tb)/tb*100:>8.1f}%{p95b:>9.0f}{p95v:>9.0f}{(p95b-p95v)/p95b*100:>8.1f}%")
PY
