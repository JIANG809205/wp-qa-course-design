#!/bin/bash
# 打印各模型 96 条 summary（简单输出，避免复杂引号）
for d in /opt/qa/s96-*; do
  [ -d "$d" ] || continue
  f="$d/summary.json"
  echo "=== $(basename "$d") ==="
  if [ -f "$f" ]; then
    cat "$f"
  else
    echo "未完成：$(ls "$d/java" 2>/dev/null | wc -l)/96"
  fi
  echo
done
