#!/bin/bash
# 兼容性测试：确保站点可用后，跑 3 视口 × 4 页面
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
DIR="/mnt/e/软件质量保证与测试课程设计/wp-compat"

if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 20); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
cd "$APP/local" && docker compose -f docker-compose.local.yml up -d 2>&1 | tail -2

code=000
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  [ "$code" = "301" ] && break
  sleep 2
done
echo "站点 HTTP=$code"

mkdir -p /opt/qa/compat
cd "$DIR" || exit 1
timeout 300 /opt/qa-venv/bin/python -u test_viewports.py 2>&1 | tail -20

if [ -d /opt/qa/compat ]; then
  cp -f /opt/qa/compat/*.png "$DIR/screenshots/" 2>/dev/null || {
    mkdir -p "$DIR/screenshots"
    cp -f /opt/qa/compat/*.png "$DIR/screenshots/"
  }
  cp -f /opt/qa/compat/compat.json "$DIR/" 2>/dev/null
  echo "截图数: $(ls "$DIR/screenshots" 2>/dev/null | wc -l)"
fi
