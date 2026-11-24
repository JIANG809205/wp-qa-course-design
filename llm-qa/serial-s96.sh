#!/bin/bash
# 串行跑 96 条：先 Flash，完成后再启动 Qwen，最后 Pro（断点续跑）
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

# 停掉除 flash 以外的进程，避免 API 限流
pkill -f "scripts96_eval.py --model qwen-plus" 2>/dev/null
pkill -f "scripts96_eval.py --model deepseek-v4-pro" 2>/dev/null
sleep 2
echo "已停止 qwen / pro，当前进程："
pgrep -af scripts96_eval.py | sed 's/^/  /'

# 后台串行调度器
nohup bash -c '
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa"
# 等 flash 跑完
while pgrep -f "scripts96_eval.py --model deepseek-v4.1-flash" >/dev/null; do sleep 30; done
echo "[调度] flash 完成，启动 qwen" >> /tmp/s96-schedule.log
/opt/qa-venv/bin/python -u scripts96_eval.py --model qwen-plus --outdir /opt/qa/s96-qwen-plus >> /tmp/s96-qwen-plus.out 2>&1
echo "[调度] qwen 完成，启动 pro" >> /tmp/s96-schedule.log
/opt/qa-venv/bin/python -u scripts96_eval.py --model deepseek-v4-pro --outdir /opt/qa/s96-deepseek-v4-pro >> /tmp/s96-deepseek-v4-pro.out 2>&1
echo "[调度] pro 完成" >> /tmp/s96-schedule.log
' > /tmp/s96-scheduler.out 2>&1 &
echo "串行调度器已启动 pid=$!"
