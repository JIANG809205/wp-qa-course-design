#!/bin/bash
# 重启 DeepSeek-V4-Pro 的评测
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
pkill -f "rigor_eval.py --model deepseek-v4-pro" 2>/dev/null
sleep 1
nohup /opt/qa-venv/bin/python -u rigor_eval.py --model deepseek-v4-pro --out summary-deepseek-v4-pro.json \
  > /tmp/rigor-deepseek-v4-pro.out 2>&1 &
echo "pro 已重启 (pid $!)"
sleep 15
tail -2 /tmp/rigor-deepseek-v4-pro.out
