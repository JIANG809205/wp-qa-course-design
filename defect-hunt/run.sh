#!/bin/bash
# 前置：确保 dockerd 与容器栈可用，然后跑缺陷探测
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
HUNT="/mnt/e/软件质量保证与测试课程设计/defect-hunt"

echo "===== 1. 环境检查 ====="
if ! docker info >/dev/null 2>&1; then
  echo "启动 dockerd..."
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
cd "$APP/local" || exit 1
docker compose -f docker-compose.local.yml up -d 2>&1 | tail -3
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"
[ "$code" != "200" ] && { echo "站点不可用"; exit 1; }

echo
echo "===== 2. 执行缺陷探测 ====="
cd "$HUNT" || exit 1
/opt/qa-venv/bin/python hunt.py 2>&1 | tail -30
