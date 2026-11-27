#!/bin/bash
# 启动 dockerd + 测试栈，并保持会话常驻
set -u
if ! docker info >/dev/null 2>&1; then
  nohup dockerd >/var/log/dockerd.log 2>&1 &
  sleep 6
fi
docker info --format 'docker={{.ServerVersion}}' || exit 1
cd "/mnt/e/软件质量保证与测试课程设计/wp-env/local" || exit 1
docker compose -f docker-compose.local.yml up -d 2>&1 | tail -4
code=000
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  if [ "$code" = "200" ] || [ "$code" = "301" ]; then break; fi
  sleep 3
done
echo "SITE=$code"
while true; do sleep 20; done
