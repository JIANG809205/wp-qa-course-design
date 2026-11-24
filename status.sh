#!/bin/bash
# 一屏看清所有后台任务状态
echo "===== 1. 性能复测 ====="
ls -1 /mnt/e/软件质量保证与测试课程设计/wp-perf/results-rigor/*.jtl 2>/dev/null | wc -l | xargs -I{} echo "已完成 jtl: {} / 9"
tail -3 /tmp/rigor-perf.log 2>/dev/null
tail -3 /tmp/rigor-*.log 2>/dev/null | tail -3

echo
echo "===== 2. 归因评测（三模型）====="
grep -E "准确率|样本分布" /tmp/triage24.out 2>/dev/null | tail -4
pgrep -af triage24_eval.py >/dev/null && echo "状态: 运行中" || echo "状态: 已结束"

echo
echo "===== 3. Rigor（Pro/Qwen）====="
for d in /opt/qa/rigor-qwen /opt/qa/rigor-pro; do
  n1=$(find "$d/cases/rep1" -name '*.json' 2>/dev/null | wc -l)
  echo "  $(basename $d) rep1: $n1 / 20"
done
pgrep -af "rigor_eval.py --model" | sed 's/^/  /'

echo
echo "===== 4. 站点 ====="
curl -sL -o /dev/null -w "首页 HTTP %{http_code}\n" -m 5 http://localhost:8080/
