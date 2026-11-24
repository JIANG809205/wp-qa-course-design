#!/bin/bash
# 校验并重启 Pro 的四分片
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
OUT=/opt/qa/s96-deepseek-v4-pro

echo "===== 1. 语法检查 ====="
/opt/qa-venv/bin/python -m py_compile scripts96_eval.py && echo "语法 OK" || { echo "语法错误"; exit 1; }

echo "===== 2. 重启四分片 ====="
pkill -f "scripts96_eval.py --model deepseek-v4-pro" 2>/dev/null
sleep 2
for i in 0 1 2 3; do
  nohup /opt/qa-venv/bin/python -u scripts96_eval.py \
    --model deepseek-v4-pro --outdir "$OUT" \
    --shard "$i" --shards 4 --max-tokens 4000 \
    > "/tmp/s96-pro-shard$i.out" 2>&1 &
  echo "分片 $i pid=$!"
done

echo "===== 3. 等待 120 秒后看速率 ====="
before=$(ls "$OUT/java" | wc -l)
sleep 120
after=$(ls "$OUT/java" | wc -l)
echo "文件数: $before → $after（120 秒内新增 $((after-before)) 条）"
if [ $((after-before)) -gt 0 ]; then
  per=$(( 120 / (after-before) ))
  echo "折合每条约 ${per} 秒；剩余 $((96-after)) 条，预计 $(( (96-after)*per/60 )) 分钟"
fi
echo "--- 各分片日志 ---"
for f in /tmp/s96-pro-shard*.out; do echo "== $(basename "$f")"; tail -1 "$f"; done
