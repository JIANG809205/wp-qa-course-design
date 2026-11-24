#!/bin/bash
# 最终收尾：重算 Pro summary → 重算保真度 → 合并三模型 → 输出 CSV
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
export WP_ROOT="/mnt/e/软件质量保证与测试课程设计/llm-qa"

echo "===== 1. 重算 Pro summary（复用已有文件，只重算指标）====="
/opt/qa-venv/bin/python -u scripts96_eval.py --model deepseek-v4-pro \
  --outdir /opt/qa/s96-deepseek-v4-pro --shard 0 --shards 4 --max-tokens 4000 2>&1 | tail -3

echo
echo "===== 2. 重算定位器保真度（n=96）====="
/opt/qa-venv/bin/python fidelity_s96.py

echo
echo "===== 3. 合并三模型 ====="
/opt/qa-venv/bin/python merge_s96.py
