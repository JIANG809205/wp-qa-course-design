#!/bin/bash
# 三模型并行跑 96 条脚本（断点续跑，输出 ext4）
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

for m in deepseek-v4.1-flash qwen-plus deepseek-v4-pro; do
  out="/opt/qa/s96-$m"
  mkdir -p "$out"
  running=$(pgrep -f "scripts96_eval.py --model $m" | head -1)
  if [ -n "${running:-}" ]; then
    echo "$m 已在运行 pid=$running"
    continue
  fi
  nohup /opt/qa-venv/bin/python -u scripts96_eval.py --model "$m" --outdir "$out" \
    > "/tmp/s96-$m.out" 2>&1 &
  echo "启动 $m pid=$!"
done

sleep 20
for f in /tmp/s96-*.out; do
  echo "== $(basename "$f")"
  tail -2 "$f"
done
