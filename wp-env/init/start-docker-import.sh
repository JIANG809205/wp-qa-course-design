#!/bin/bash
# 启动 dockerd（setsid 脱离会话，避免被任务管理连带杀掉）+ 导入基础镜像
set -u

if docker info >/dev/null 2>&1; then
  echo "dockerd already running"
else
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
echo "===== 导入 rootfs 为镜像 ====="
if docker image inspect ubuntu:jammy-local >/dev/null 2>&1; then
  echo "镜像已存在"
else
  tar -C /opt/rootfs -c . | docker import - ubuntu:jammy-local
  echo "import_exit=$?"
fi

echo
echo "===== 验证容器可运行 ====="
docker run --rm --network host ubuntu:jammy-local bash -c 'head -2 /etc/os-release; echo CONTAINER_OK'
echo
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
