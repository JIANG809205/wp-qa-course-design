#!/bin/bash
# 重启 dockerd 应用镜像配置，并拉取课程设计所需镜像
set -u

pkill -9 dockerd 2>/dev/null
sleep 2
rm -f /var/run/docker.pid
nohup dockerd >/var/log/dockerd.log 2>&1 &
for i in $(seq 1 30); do
  sleep 2
  docker info >/dev/null 2>&1 && break
done
echo "dockerd: $(docker info --format '{{.ServerVersion}}')"
docker info 2>/dev/null | sed -n '/Registry Mirrors/,+2p'

pull() {
  img="$1"
  if docker image inspect "$img" >/dev/null 2>&1; then
    echo "== $img 已存在"
    return 0
  fi
  printf '== pulling %-26s ... ' "$img"
  if timeout 900 docker pull "$img" >/tmp/p.log 2>&1; then
    echo "OK"
    return 0
  else
    echo "FAIL"
    tail -2 /tmp/p.log | cut -c1-110
    return 1
  fi
}

echo
echo "===== 基础镜像 ====="
pull redis:7-alpine
pull mariadb:11

echo
echo "===== WordPress（优先 7.1.5，失败回落 6.6.2）====="
if pull wordpress:7.1.5; then
  echo "WP_VERSION=7.1.5" > /tmp/wp_version
else
  pull wordpress:6.6.2 && echo "WP_VERSION=6.6.2" > /tmp/wp_version
fi
cat /tmp/wp_version 2>/dev/null

echo
echo "===== wp-cli ====="
pull wordpress:cli-php8.2 || pull wordpress:cli

echo
echo "===== 现有镜像 ====="
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
