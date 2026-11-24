#!/bin/bash
# 只重启 Qwen 的评测（flash 与 pro 仍在跑，不动它们）
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

pkill -f "rigor_eval.py --model qwen-plus" 2>/dev/null
sleep 1
nohup /opt/qa-venv/bin/python -u rigor_eval.py --model qwen-plus --out summary-qwen-plus.json \
  > /tmp/rigor-qwen-plus.out 2>&1 &
echo "qwen 已重启 (pid $!)"
sleep 20
tail -3 /tmp/rigor-qwen-plus.out
