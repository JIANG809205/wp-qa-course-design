#!/bin/bash
# 测试各模型是否返回 content（有些推理模型把内容放在 reasoning_content）
set -u
ENV_FILE="/mnt/e/软件质量保证与测试课程设计/llm-qa/.env"
KEY=$(sed -n 's/^DASHSCOPE_API_KEY=//p' "$ENV_FILE" | tr -d '\r')
BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"

for m in deepseek-v4.1-flash deepseek-v4-pro qwen-plus vanchin/deepseek-r1; do
  echo "===== $m ====="
  curl -s -m 90 -o /tmp/r.json -w 'HTTP %{http_code}\n' "$BASE/chat/completions" \
    -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"用 JSON 数组输出两条测试用例，字段 id,title\"}],\"max_tokens\":300}"
  python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/r.json'))
except Exception as e:
    print('  解析失败:', e); raise SystemExit
if 'error' in d:
    print('  ERROR:', d['error'].get('message', d['error']))
else:
    msg = d['choices'][0].get('message', {})
    print('  content 长度:', len(msg.get('content') or ''))
    print('  reasoning 长度:', len(msg.get('reasoning_content') or ''))
    print('  预览:', ((msg.get('content') or msg.get('reasoning_content') or '')[:120]).replace('\n', ' '))
    print('  finish_reason:', d['choices'][0].get('finish_reason'))
    print('  usage:', d.get('usage'))
PY
done
