#!/bin/bash
# 启动测试栈并等待站点就绪
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env/local"
cd "$APP" || exit 1
docker compose -f docker-compose.local.yml up -d 2>&1 | tail -8
code=000
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  if [ "$code" = "200" ]; then break; fi
  sleep 3
done
echo "SITE_HTTP=$code"
docker ps --format '{{.Names}} {{.Status}}'
