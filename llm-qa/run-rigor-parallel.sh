#!/bin/bash
# 三个模型并行跑严谨评测
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
rm -rf outputs/rigor
mkdir -p outputs/rigor

for m in deepseek-v4.1-flash deepseek-v4-pro qwen-plus; do
  nohup /opt/qa-venv/bin/python -u rigor_eval.py --model "$m" --out "summary-$m.json" \
    > "/tmp/rigor-$m.out" 2>&1 &
  echo "启动 $m (pid $!)"
done

sleep 30
echo "--- 30 秒后进度 ---"
for f in /tmp/rigor-*.out; do
  echo "== $f"
  tail -2 "$f"
done
