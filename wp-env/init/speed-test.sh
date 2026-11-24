#!/bin/bash
# 镜像源测速（逐个小镜像实测，测试间清空缓存保证可比）
IMG=redis:7-alpine

for m in hub.rat.dev docker.xuanyuan.me docker.1panel.live; do
  echo "===== $m ====="
  docker rmi "$m/library/$IMG" >/dev/null 2>&1
  docker builder prune -af >/dev/null 2>&1
  start=$(date +%s)
  if timeout 150 docker pull "$m/library/$IMG" >/tmp/mirror-speed.log 2>&1; then
    end=$(date +%s)
    sz=$(docker image inspect "$m/library/$IMG" --format '{{.Size}}' 2>/dev/null || echo 0)
    echo "OK  $((end - start))s  size=$((sz / 1024 / 1024))MB  rate=$((sz / 1024 / (end - start + 1)))KB/s"
  else
    echo "FAIL $(( $(date +%s) - start ))s"
    tail -2 /tmp/mirror-speed.log
  fi
done
