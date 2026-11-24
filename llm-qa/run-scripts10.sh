#!/bin/bash
# 后台跑脚本生成评测（10 条/模型），输出到 ext4
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
mkdir -p /opt/qa/scripts10
OUT_DIR=/opt/qa/scripts10 nohup /opt/qa-venv/bin/python -u scripts10_eval.py \
  > /tmp/scripts10.out 2>&1 &
echo "scripts10 启动 pid=$!"
sleep 15
tail -3 /tmp/scripts10.out
