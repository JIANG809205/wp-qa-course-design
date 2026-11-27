#!/bin/bash
# 真实执行：准备鉴权 → 跑 26 条 pytest 接口用例
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计"
cd "$ROOT/wp-api-tests" || exit 1
bash setup-all-auth.sh 2>&1 | tail -5
echo "=== pytest ==="
WP_BASE=http://localhost:8080 /opt/qa-venv/bin/python -m pytest -q 2>&1 | tail -18
