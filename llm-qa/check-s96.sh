#!/bin/bash
# 查看 96 条脚本评测进度
for f in /tmp/s96-deepseek-v4.1-flash.out /tmp/s96-qwen-plus.out /tmp/s96-deepseek-v4-pro.out; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .out)
  printf '%-32s ' "$name"
  tail -1 "$f"
done

echo "--- 已生成 java 数 ---"
for d in /opt/qa/s96-*; do
  [ -d "$d" ] || continue
  n=$(ls "$d/java" 2>/dev/null | wc -l)
  echo "$(basename "$d"): $n / 96"
done

echo "--- 进程 ---"
pgrep -af scripts96_eval.py | wc -l
