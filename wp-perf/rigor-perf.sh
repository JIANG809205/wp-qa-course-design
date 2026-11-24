#!/bin/bash
# 严谨版性能测试：3 个并发级别 × 3 次重复 × 单轮 60 秒，并采样容器 CPU
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
WORK=/opt/qa/wp-perf
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar
OUT="$ROOT/results-rigor"

mkdir -p "$OUT"
cp "$ROOT/jmx/perf-duration.jmx" "$WORK/jmx/" 2>/dev/null

# 站点检查
code=$(curl -sL -o /dev/null -w '%{http_code}' -m 5 http://localhost:8080/ || echo 000)
echo "站点 HTTP=$code"
[ "$code" != "200" ] && { echo "站点不可用"; exit 1; }

sample_cpu() {
  # 后台采样 wp-app 的 CPU%，每 2 秒一次，写入文件
  local f="$1" stop="$2"
  : > "$f"
  while [ ! -f "$stop" ]; do
    docker stats --no-stream --format '{{.CPUPerc}}' wp-app 2>/dev/null | tr -d '%' >> "$f"
    sleep 2
  done
}

for threads in 10 50 100; do
  for rep in 1 2 3; do
    jtl="/tmp/rigor-$threads-$rep.jtl"
    cpuf="/tmp/cpu-$threads-$rep.txt"
    stopf="/tmp/stop-$threads-$rep"
    rm -f "$jtl" "$stopf"
    sample_cpu "$cpuf" "$stopf" &
    sampler=$!

    cd /opt || exit 1
    timeout 300 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
      -jar "$JM" -n -t "$WORK/jmx/perf-duration.jmx" -l "$jtl" \
      -Jpath="/" -Jthreads="$threads" -Jramp=10 -Jduration=60 >"/tmp/rigor-$threads-$rep.log" 2>&1

    touch "$stopf"
    wait $sampler 2>/dev/null

    if [ -s "$jtl" ]; then
      cp "$jtl" "$OUT/home-$threads-rep$rep.jtl"
      cpu=$(awk '{s+=$1; n++} END {if(n>0) printf "%.1f", s/n; else print "NA"}' "$cpuf")
      echo "  threads=$threads rep=$rep 完成，平均 CPU=${cpu}%"
      echo "$threads,$rep,$cpu" >> "$OUT/cpu.csv"
    else
      echo "  threads=$threads rep=$rep 失败"
      tail -2 "/tmp/rigor-$threads-$rep.log"
    fi
  done
done

echo
echo "===== 汇总（3 次取中位数）====="
python3 - <<'PY'
import csv, glob, os, statistics

OUT = "/mnt/e/软件质量保证与测试课程设计/wp-perf/results-rigor"

def metrics(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8", errors="replace")))
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts) - min(ts), 1) / 1000
    n = len(rows)
    err = sum(1 for r in rows if str(r["success"]).lower() != "true")
    return n / dur, statistics.mean(el), el[int(0.95 * n) - 1], err * 100 / n

print(f"{'并发':<6}{'TPS(中位)':>10}{'TPS范围':>18}{'平均RT':>9}{'P95(中位)':>11}{'错误率':>8}")
for t in (10, 50, 100):
    files = sorted(glob.glob(os.path.join(OUT, f"home-{t}-rep*.jtl")))
    if not files:
        continue
    ms = [metrics(f) for f in files]
    tps = [m[0] for m in ms]
    p95 = [m[2] for m in ms]
    print(f"{t:<6}{statistics.median(tps):>10.1f}{'  ' + f'{min(tps):.0f}~{max(tps):.0f}':>18}"
          f"{statistics.mean([m[1] for m in ms]):>9.0f}{statistics.median(p95):>11.0f}"
          f"{statistics.mean([m[3] for m in ms]):>7.2f}%")
PY
