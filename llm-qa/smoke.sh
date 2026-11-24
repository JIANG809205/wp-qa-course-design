#!/bin/bash
# 语法检查 + 单模型冒烟
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

echo "===== 1. 语法检查 ====="
/opt/qa-venv/bin/python -c "import ast; ast.parse(open('run.py').read()); ast.parse(open('llm_qa.py').read()); print('syntax ok')"

echo
echo "===== 2. 单模型冒烟（deepseek-v4.1-flash，仅用例任务）====="
timeout 300 /opt/qa-venv/bin/python run.py --provider dashscope \
  --model deepseek-v4.1-flash --task cases --out outputs/smoke-flash 2>&1 | tail -8

echo
echo "===== 3. 产物检查 ====="
ls -l outputs/smoke-flash/cases/*.json 2>/dev/null | head -3
head -c 400 outputs/smoke-flash/cases/R01.json 2>/dev/null
echo
