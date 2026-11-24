#!/bin/bash
# 验证 API key：不打印 key，只打印状态码与错误摘要
set -u
ENV_FILE="/mnt/e/软件质量保证与测试课程设计/llm-qa/.env"
KEY=$(sed -n 's/^DEEPSEEK_API_KEY=//p' "$ENV_FILE" | tr -d '\r')
echo "key length: ${#KEY}"
echo "key prefix: ${KEY:0:6}..."

probe() {
  url="$1"
  echo "--- $url ---"
  code=$(curl -s -o /tmp/probe.json -w '%{http_code}' -m 25 "$url" -H "Authorization: Bearer $KEY")
  echo "HTTP $code"
  head -c 300 /tmp/probe.json 2>/dev/null
  echo
}

probe "https://api.deepseek.com/models"
probe "https://api.deepseek.com/v1/models"

echo "--- chat/completions 最小请求 ---"
curl -s -o /tmp/chat.json -w 'HTTP %{http_code}\n' -m 40 \
  https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"回复 OK 两个字母"}],"max_tokens":10}'
head -c 400 /tmp/chat.json
echo
