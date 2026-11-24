#!/bin/bash
# 查看 96 条各模型 summary，并重启未完成的模型（串行）
set -u
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1

echo "===== 各模型状态 ====="
for d in /opt/qa/s96-*; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  n=$(ls "$d/java" 2>/dev/null | wc -l)
  sum="-"
  [ -f "$d/summary.json" ] && sum=$(/opt/qa-venv/bin/python -c "
import json,sys
d=json.load(open('$d/summary.json'))
print(f\"n={d['n']} 结构={d['struct_rate']}% 严格={d['strict_rate']}% CI={d['strict_ci']}\")
" 2>/dev/null || echo "解析失败")
  printf '%-30s java=%3s/96  %s\n' "$name" "$n" "$sum"
done

echo
echo "===== 重启未完成模型（串行）====="
for m in qwen-plus deepseek-v4-pro; do
  out="/opt/qa/s96-$m"
  cnt=$(ls "$out/java" 2>/dev/null | wc -l)
  if [ "$cnt" -ge 96 ]; then
    echo "$m 已完成，跳过"
    continue
  fi
  if pgrep -f "scripts96_eval.py --model $m" >/dev/null; then
    echo "$m 正在运行"
    continue
  fi
  nohup /opt/qa-venv/bin/python -u scripts96_eval.py --model "$m" --outdir "$out" \
    >> "/tmp/s96-$m.out" 2>&1 &
  echo "启动 $m（已有 $cnt 条，断点续跑）pid=$!"
  # 串行：等它结束再下一个
  while pgrep -f "scripts96_eval.py --model $m" >/dev/null; do sleep 30; done
  echo "$m 结束"
done
echo "全部完成"
