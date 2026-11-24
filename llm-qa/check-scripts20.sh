#!/bin/bash
# 查看 20 条脚本评测进度
for f in /tmp/scripts20-deepseek-v4.1-flash.out /tmp/scripts20-deepseek-v4-pro.out /tmp/scripts20-qwen-plus.out; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .out)
  done_lines=$(grep -c "n=20" "$f" 2>/dev/null || true)
  printf '%-34s 完成模型数=%s  ' "$name" "${done_lines:-0}"
  tail -1 "$f"
done
echo "--- summary 文件 ---"
ls -1 /opt/qa/scripts20-*/scripts20-summary.json 2>/dev/null || echo "尚无"
