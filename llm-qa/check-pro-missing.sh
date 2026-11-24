#!/bin/bash
# 检查 Pro 是否 96 条齐、缺哪些
D=/opt/qa/s96-deepseek-v4-pro
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
echo "已完成: $(ls "$D/java" | wc -l) / 96"
echo "运行中的分片数: $(pgrep -f 'scripts96_eval.py --model deepseek-v4-pro' | wc -l)"
/opt/qa-venv/bin/python - <<'PY'
import json, os
specs = json.load(open("data/scripts96.json", encoding="utf-8"))
have = {f.replace(".java", "") for f in os.listdir("/opt/qa/s96-deepseek-v4-pro/java")}
missing = [s["id"] for s in specs if s["id"] not in have]
print("缺失", len(missing), "条:", missing[:10])
PY
echo "--- 分片日志尾 ---"
for f in /tmp/s96-pro-shard*.out; do echo "== $(basename "$f")"; tail -2 "$f"; done
