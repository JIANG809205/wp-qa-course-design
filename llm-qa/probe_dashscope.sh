#!/bin/bash
# 验证百炼（DashScope）OpenAI 兼容端点
set -u
ENV_FILE="/mnt/e/软件质量保证与测试课程设计/llm-qa/.env"
KEY=$(sed -n 's/^DASHSCOPE_API_KEY=//p' "$ENV_FILE" | tr -d '\r')
[ -z "$KEY" ] && KEY=$(sed -n 's/^DEEPSEEK_API_KEY=//p' "$ENV_FILE" | tr -d '\r')
echo "key length=${#KEY} prefix=${KEY:0:6}..."

BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"

echo "=== 1. /models ==="
code=$(curl -s -o /tmp/ds_models.json -w '%{http_code}' -m 25 "$BASE/models" -H "Authorization: Bearer $KEY")
echo "HTTP $code"
python3 -c "
import json
d=json.load(open('/tmp/ds_models.json'))
ids=[m['id'] for m in d.get('data',[])]
print('模型数:', len(ids))
print([i for i in ids if 'qwen' in i or 'deepseek' in i][:12])
" 2>/dev/null || head -c 300 /tmp/ds_models.json

echo
echo "=== 2. chat: qwen-plus ==="
curl -s -o /tmp/ds_chat.json -w 'HTTP %{http_code}\n' -m 40 \
  "$BASE/chat/completions" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"只回复两个字：正常"}],"max_tokens":20}'
python3 -c "
import json
d=json.load(open('/tmp/ds_chat.json'))
print('回复:', d['choices'][0]['message']['content'])
print('用量:', d.get('usage'))
" 2>/dev/null || head -c 300 /tmp/ds_chat.json

echo
echo "=== 3. chat: deepseek-v3 ==="
curl -s -o /tmp/ds_chat2.json -w 'HTTP %{http_code}\n' -m 60 \
  "$BASE/chat/completions" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v3","messages":[{"role":"user","content":"只回复两个字：正常"}],"max_tokens":20}'
python3 -c "
import json
d=json.load(open('/tmp/ds_chat2.json'))
print('回复:', d['choices'][0]['message']['content'])
" 2>/dev/null || head -c 300 /tmp/ds_chat2.json
