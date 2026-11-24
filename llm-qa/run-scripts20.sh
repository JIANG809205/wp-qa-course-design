#!/bin/bash
# 三模型并行跑 20 条脚本样本，输出写 ext4
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

for m in deepseek-v4.1-flash deepseek-v4-pro qwen-plus; do
  mkdir -p "/opt/qa/scripts20-$m"
  OUT_DIR="/opt/qa/scripts20-$m" nohup /opt/qa-venv/bin/python -u scripts20_eval.py \
    --model "$m" > "/tmp/scripts20-$m.out" 2>&1 &
  echo "启动 $m pid=$!"
done

sleep 20
for f in /tmp/scripts20-*.out; do
  echo "== $(basename "$f")"
  tail -2 "$f"
done
