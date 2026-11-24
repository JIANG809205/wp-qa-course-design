#!/bin/bash
# 文章列表页性能复测：3 级并发 × 3 次 × 60 秒，用于与旧数据可比
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
WORK=/opt/qa/wp-perf
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar
OUT="$ROOT/results-rigor-blog"
PATHQ="/qa-blog/"

mkdir -p "$OUT"
code=$(curl -sL -o /dev/null -w '%{http_code}' -m 5 "http://localhost:8080$PATHQ" || echo 000)
echo "列表页 HTTP=$code"
[ "$code" != "200" ] && { echo "列表页不可用"; exit 1; }

sample_cpu() {
  local f="$1" stop="$2"
  : > "$f"
  while [ ! -f "$stop" ]; do
    docker stats --no-stream --format '{{.CPUPerc}}' wp-app 2>/dev/null | tr -d '%' >> "$f"
    sleep 2
  done
}

for threads in 10 50 100; do
  for rep in 1 2 3; do
    jtl="/tmp/list-$threads-$rep.jtl"
    cpuf="/tmp/listcpu-$threads-$rep.txt"
    stopf="/tmp/liststop-$threads-$rep"
    rm -f "$jtl" "$stopf"
    sample_cpu "$cpuf" "$stopf" &
    sampler=$!

    cd /opt || exit 1
    timeout 300 java -Djmeter.home=/opt/apache-jmeter-5.6.3 -jar "$JM" -n \
      -t "$WORK/jmx/perf-duration.jmx" -l "$jtl" \
      -Jpath="$PATHQ" -Jthreads="$threads" -Jramp=10 -Jduration=60 \
      >"/tmp/list-$threads-$rep.log" 2>&1
    touch "$stopf"
    wait $sampler 2>/dev/null

    if [ -s "$jtl" ]; then
      cp "$jtl" "$OUT/list-$threads-rep$rep.jtl"
      cpu=$(awk '{s+=$1;n++} END {if(n>0) printf "%.1f", s/n; else print "NA"}' "$cpuf")
      echo "  threads=$threads rep=$rep 平均CPU=${cpu}%"
      echo "$threads,$rep,$cpu" >> "$OUT/cpu.csv"
    else
      echo "  threads=$threads rep=$rep 失败"
    fi
  done
done

echo
echo "===== 列表页汇总（3 次取中位数）====="
python3 - <<'PY'
import csv, glob, os, statistics
OUT = "/mnt/e/软件质量保证与测试课程设计/wp-perf/results-rigor-list"
def metrics(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8", errors="replace")))
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000
    n = len(rows)
    err = sum(1 for r in rows if str(r["success"]).lower() != "true")
    return n / dur, statistics.mean(el), el[int(0.95*n)-1], err*100/n
print(f"{'并发':<6}{'TPS(中位)':>10}{'范围':>16}{'平均RT':>9}{'P95':>7}{'错误率':>8}")
for t in (10, 50, 100):
    fs = sorted(glob.glob(os.path.join(OUT, f"list-{t}-rep*.jtl")))
    if not fs: continue
    ms = [metrics(f) for f in fs]
    tps = [m[0] for m in ms]; p95 = [m[2] for m in ms]
    print(f"{t:<6}{statistics.median(tps):>10.1f}{f'{min(tps):.0f}~{max(tps):.0f}':>16}"
          f"{statistics.mean([m[1] for m in ms]):>9.0f}{statistics.median(p95):>7.0f}"
          f"{statistics.mean([m[3] for m in ms]):>7.2f}%")
PY
