#!/bin/bash
# 交错对照：同一时段内交替跑 A/B/A/B/A/B，排除时间漂移对两场景对比的影响
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"
JM=/opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar
OUT="$ROOT/results-interleaved"
mkdir -p "$OUT"

run_one() {
  local tag="$1" path="$2" rep="$3"
  local jtl="/tmp/il-$tag-$rep.jtl"
  rm -f "$jtl"
  cd /opt || return 1
  timeout 240 java -Djmeter.home=/opt/apache-jmeter-5.6.3 -jar "$JM" -n \
    -t /opt/qa/wp-perf/jmx/perf-duration.jmx -l "$jtl" \
    -Jpath="$path" -Jthreads=50 -Jramp=10 -Jduration=60 \
    >"/tmp/il-$tag-$rep.log" 2>&1
  if [ -s "$jtl" ]; then
    cp "$jtl" "$OUT/$tag-rep$rep.jtl"
    echo "  $tag rep$rep 完成"
  else
    echo "  $tag rep$rep 失败"
  fi
}

echo "交错运行：首页(A) / 列表(B) 各 3 次，单轮 60 秒，50 并发"
for rep in 1 2 3; do
  run_one "home" "/" "$rep"
  run_one "list" "/?page_id=1054" "$rep"
done

echo
echo "===== 交错结果 ====="
python3 - <<'PY'
import csv, glob, os, statistics
OUT = "/mnt/e/软件质量保证与测试课程设计/wp-perf/results-interleaved"
def m(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8", errors="replace")))
    el = sorted(float(r["elapsed"]) for r in rows)
    ts = [int(r["timeStamp"]) for r in rows]
    dur = max(max(ts)-min(ts),1)/1000
    n = len(rows)
    return n/dur, el[int(0.95*n)-1]
for tag, label in (("home","静态首页"), ("list","文章列表页")):
    fs = sorted(glob.glob(os.path.join(OUT, f"{tag}-rep*.jtl")))
    if not fs: continue
    vals = [m(f) for f in fs]
    tps = [v[0] for v in vals]; p95 = [v[1] for v in vals]
    print(f"{label:<10} TPS 中位 {statistics.median(tps):.1f}  各次 {[round(t,1) for t in tps]}  "
          f"P95 中位 {statistics.median(p95):.0f}ms")
PY
