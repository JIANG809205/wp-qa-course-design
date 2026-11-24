#!/bin/bash
# 正确统计进度：用例文件名为 F01..F20.json
for d in /opt/qa/rigor-qwen /opt/qa/rigor-pro; do
  echo "===== $d ====="
  for rep in rep1 rep2 rep3; do
    n=$(find "$d/cases/$rep" -name '*.json' 2>/dev/null | wc -l)
    echo "  $rep: $n / 20"
  done
  echo "  scripts: $(find "$d/scripts" -name '*.java' 2>/dev/null | wc -l) / 10"
  [ -f "$d/summary-qwen-plus.json" ] && echo "  summary(qwen) 已生成"
  [ -f "$d/summary-deepseek-v4-pro.json" ] && echo "  summary(pro) 已生成"
done

echo
echo "===== 日志尾部 ====="
tail -4 /tmp/rigor-qwen-plus.out
echo "---"
tail -4 /tmp/rigor-deepseek-v4-pro.out
