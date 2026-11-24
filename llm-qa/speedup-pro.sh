#!/bin/bash
# Pro 提速：4 分片并行 + 限制输出预算
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
OUT=/opt/qa/s96-deepseek-v4-pro

pkill -f "scripts96_eval.py --model deepseek-v4-pro" 2>/dev/null
sleep 2

for i in 0 1 2 3; do
  nohup /opt/qa-venv/bin/python -u scripts96_eval.py \
    --model deepseek-v4-pro --outdir "$OUT" \
    --shard "$i" --shards 4 --max-tokens 4000 \
    > "/tmp/s96-pro-shard$i.out" 2>&1 &
  echo "分片 $i 启动 pid=$!"
done

sleep 90
echo "--- 90 秒后进度 ---"
echo "java 文件数: $(ls "$OUT/java" | wc -l) / 96"
for f in /tmp/s96-pro-shard*.out; do
  echo "== $(basename "$f")"
  tail -1 "$f"
done
