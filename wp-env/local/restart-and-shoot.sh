#!/bin/bash
# 重启 Docker 栈并抓取三张截图
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
COMPOSE="$APP/local/docker-compose.local.yml"

echo "===== 1. dockerd ====="
if docker info >/dev/null 2>&1; then
  echo "running $(docker info --format '{{.ServerVersion}}')"
else
  pkill -9 dockerd 2>/dev/null
  sleep 2
  rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && break; done
  echo "started $(docker info --format '{{.ServerVersion}}' 2>&1)"
fi

echo
echo "===== 2. 保活 + 起栈 ====="
pgrep -f dsh-wp-keepalive >/dev/null 2>&1 || setsid nohup bash -c 'exec -a dsh-wp-keepalive sleep infinity' >/dev/null 2>&1 &
cd "$APP/local" || exit 1
docker compose -f "$COMPOSE" up -d 2>&1 | tail -4
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done
echo "首页 HTTP=$code"

echo
echo "===== 3. 截图 ====="
cp "$APP/local/screenshot.py" /opt/qa/screenshot.py
cd /opt/qa || exit 1
timeout 180 /opt/qa-venv/bin/python -u screenshot.py 2>&1 | tail -8
ls -lh /opt/qa/shot-*.png 2>/dev/null || echo "无截图"

echo
echo "===== 4. 复制到工作区 ====="
SHOTS="$APP/screenshots"
mkdir -p "$SHOTS"
cp -f /opt/qa/shot-*.png "$SHOTS"/ 2>/dev/null && ls -lh "$SHOTS"
