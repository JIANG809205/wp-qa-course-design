#!/bin/bash
# 查看三个并行评测的进度
for f in /tmp/rigor-deepseek-v4.1-flash.out /tmp/rigor-deepseek-v4-pro.out /tmp/rigor-qwen-plus.out; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .out)
  reps=$(grep -c "rep" "$f" 2>/dev/null || echo 0)
  printf '%-30s rep进度=%s  ' "$name" "$reps"
  tail -1 "$f"
done

echo "--- 已生成 JSON 数 ---"
find "/mnt/e/软件质量保证与测试课程设计/llm-qa/outputs/rigor" -type f 2>/dev/null | wc -l

echo "--- 进程 ---"
pgrep -af rigor_eval.py | head -5
