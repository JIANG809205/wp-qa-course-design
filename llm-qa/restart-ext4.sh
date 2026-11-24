#!/bin/bash
# 重启 Qwen 与 Pro 的评测，输出写到 ext4（/opt），避免 /mnt/e 长写 I/O 错误
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

pkill -f "rigor_eval.py --model qwen-plus" 2>/dev/null
pkill -f "rigor_eval.py --model deepseek-v4-pro" 2>/dev/null
sleep 2

mkdir -p /opt/qa/rigor-qwen /opt/qa/rigor-pro

RIGOR_OUT=/opt/qa/rigor-qwen nohup /opt/qa-venv/bin/python -u rigor_eval.py \
  --model qwen-plus --out summary-qwen-plus.json > /tmp/rigor-qwen-plus.out 2>&1 &
echo "qwen 启动 pid=$!"

RIGOR_OUT=/opt/qa/rigor-pro nohup /opt/qa-venv/bin/python -u rigor_eval.py \
  --model deepseek-v4-pro --out summary-deepseek-v4-pro.json > /tmp/rigor-deepseek-v4-pro.out 2>&1 &
echo "pro 启动 pid=$!"

sleep 25
for f in /tmp/rigor-qwen-plus.out /tmp/rigor-deepseek-v4-pro.out; do
  echo "== $f"
  tail -2 "$f"
done
