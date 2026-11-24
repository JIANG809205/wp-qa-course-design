#!/bin/bash
# 启动 dockerd 并检查镜像（官方 wordpress 镜像是否已拉取成功）
set -u
if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null
  sleep 2
  rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do
    sleep 2
    docker info >/dev/null 2>&1 && break
  done
fi
echo "dockerd: $(docker info --format '{{.ServerVersion}}' 2>&1)"

echo
echo "===== 镜像清单 ====="
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}' | sort

echo
echo "===== 是否为官方镜像 ====="
if docker image inspect wordpress:7.1.5 >/dev/null 2>&1; then
  echo "官方 wordpress:7.1.5 已存在"
  docker image inspect wordpress:7.1.5 --format '{{.Created}} {{index .Config.Labels "org.opencontainers.image.version"}}'
else
  echo "官方镜像不存在，需要拉取"
fi
