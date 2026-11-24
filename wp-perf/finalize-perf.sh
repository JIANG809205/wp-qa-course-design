#!/bin/bash
# 收尾：确认响应头/缓存是否生效，并汇总三方对比
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计/wp-perf"

echo "===== 1. 前台响应头 ====="
curl -sI http://127.0.0.1:8080/ | grep -iE "vary|cache-control|expires|x-cache" || echo "无缓存相关头"

echo
echo "===== 2. mod_cache 是否真的写盘 ====="
docker exec wp-app du -sh /var/cache/apache2/mod_cache_disk 2>/dev/null
docker exec wp-app bash -c 'find /var/cache/apache2/mod_cache_disk -type f 2>/dev/null | wc -l'

echo
echo "===== 3. 对比汇总 ====="
python3 - <<'PY'
import csv, os, statistics

def m(p):
    rows = list(csv.DictReader(open(p, encoding='utf-8', errors='replace')))
    el = sorted(float(r['elapsed']) for r in rows)
    ts = [int(r['timeStamp']) for r in rows]
    dur = max(max(ts)-min(ts), 1)/1000
    return len(rows)/dur, statistics.mean(el), el[int(0.95*len(rows))-1]

base = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results'
tuned = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-tuned'
cache = '/mnt/e/软件质量保证与测试课程设计/wp-perf/results-cache'

print(f"{'并发':<5}{'基线TPS':>8}{'参数调优':>9}{'页面缓存':>9}{'基线P95':>8}{'调优P95':>8}{'缓存P95':>8}")
for t in (100, 200):
    files = {
        'b': os.path.join(base, f'home-{t}.jtl'),
        'v': os.path.join(tuned, f'home-{t}.jtl'),
        'c': os.path.join(cache, f'home-{t}.jtl'),
    }
    vals = {}
    for k, p in files.items():
        vals[k] = m(p) if os.path.exists(p) else (0, 0, 0)
    tb, ab, pb = vals['b']; tv, av, pv = vals['v']; tc, ac, pc = vals['c']
    s = lambda x: f"{x:>9.1f}" if x else f"{'—':>9}"
    sp = lambda x: f"{x:>8.0f}" if x else f"{'—':>8}"
    print(f"{t:<5}{tb:>8.1f}{s(tv)}{s(tc)}{pb:>8.0f}{sp(pv)}{sp(pc)}")
PY
