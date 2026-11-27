#!/bin/bash
# 现场复跑：首页与列表页各 10 并发 60 秒一轮，检验稳态 TPS 是否与报告一致
set -u
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar
WORK=/opt/qa/wp-perf/jmx/perf-duration.jmx
cd /opt || exit 1
for name in home list; do
  if [ "$name" = "home" ]; then path="/"; else path="/qa-blog/"; fi
  jtl=/tmp/verify-$name.jtl
  timeout 150 java -Djmeter.home=/opt/apache-jmeter-5.6.3 -jar "$JM" -n \
    -t "$WORK" -l "$jtl" -Jpath="$path" -Jthreads=10 -Jramp=10 -Jduration=60 \
    >/tmp/verify-$name.log 2>&1
  echo "=== $name ($path) ==="
  /opt/qa-venv/bin/python - "$jtl" <<'PY'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8', errors='replace')))
ts = [int(r['timeStamp']) for r in rows]
t0, t1 = min(ts), max(ts)
steady = [r for r in rows if int(r['timeStamp']) >= t0 + 10000]
el = sorted(float(r['elapsed']) for r in steady)
dur = max((t1 - (t0 + 10000)) / 1000, 1)
p95 = el[max(int(round(0.95 * len(el))) - 1, 0)]
print(f"总样本={len(rows)} 稳态样本={len(steady)} 稳态时长={dur:.1f}s "
      f"TPS={len(steady)/dur:.1f} P95={p95:.0f}ms")
PY
done
