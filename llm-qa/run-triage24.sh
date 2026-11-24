#!/bin/bash
# 启动 24 条平衡样本的归因评测（三模型）
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
mkdir -p /opt/qa/rigor-triage
RIGOR_OUT=/opt/qa/rigor-triage nohup /opt/qa-venv/bin/python -u triage24_eval.py \
  > /tmp/triage24.out 2>&1 &
echo "triage24 启动 pid=$!"
sleep 20
tail -5 /tmp/triage24.out
