#!/bin/bash
# 估算 Pro 的生成速率与剩余时间
D=/opt/qa/s96-deepseek-v4-pro
n=$(ls "$D/java" 2>/dev/null | wc -l)
echo "已完成: $n / 96"
if [ "$n" -ge 2 ]; then
  first=$(ls -t "$D/java" | tail -1)
  last=$(ls -t "$D/java" | head -1)
  t1=$(stat -c %Y "$D/java/$first")
  t2=$(stat -c %Y "$D/java/$last")
  span=$(( t2 - t1 ))
  avg=$(( span / (n - 1) ))
  remain=$(( (96 - n) * avg ))
  echo "首条: $first  末条: $last"
  echo "平均每条: ${avg} 秒"
  echo "剩余 $((96-n)) 条，预计 $((remain/60)) 分钟"
else
  echo "样本不足，无法估算"
fi
echo "--- 进程 ---"
pgrep -af "scripts96_eval.py --model deepseek-v4-pro" | head -2
