#!/bin/bash
# 一次性：起 dockerd → 起容器栈 → 校验站点 → 截图
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"

if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null
  sleep 2
  rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 20); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
echo "dockerd: $(docker info --format '{{.ServerVersion}}' 2>&1)"

cd "$APP/local" || exit 1
docker compose -f docker-compose.local.yml up -d 2>&1 | tail -3

code=000
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 2
done
echo "首页 HTTP=$code"

echo "--- 站点状态 ---"
echo "版本: $(docker exec -u www-data wp-app wp core version 2>/dev/null)"
echo "语言: $(docker exec -u www-data wp-app wp language core list --status=active --field=language 2>/dev/null)"
echo "首页模式: $(docker exec -u www-data wp-app wp option get show_on_front 2>/dev/null) id=$(docker exec -u www-data wp-app wp option get page_on_front 2>/dev/null)"
echo "文章数: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count 2>/dev/null)"

echo "--- 截图 ---"
cd /opt/qa && cp "$APP/local/screenshot.py" /opt/qa/screenshot.py 2>/dev/null
timeout 120 /opt/qa-venv/bin/python -u screenshot.py 2>&1 | tail -4
cp -f /opt/qa/shot-*.png "$APP/screenshots/" 2>/dev/null
ls -lh "$APP/screenshots/" | tail -4
