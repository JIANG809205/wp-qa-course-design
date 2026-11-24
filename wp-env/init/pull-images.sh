#!/bin/bash
# 拉取课程设计所需镜像（通过 hub.rat.dev 加速）
set -u
IMAGES="mariadb:11 redis:7-alpine wordpress:6.6.2 wordpress:6.6.1 wordpress:cli-php8.2"

for img in $IMAGES; do
  if docker image inspect "$img" >/dev/null 2>&1; then
    echo "== $img already present"
    continue
  fi
  printf '== pulling %-28s ... ' "$img"
  if timeout 900 docker pull "$img" >/tmp/pull-one.log 2>&1; then
    echo OK
  else
    echo FAIL
    tail -3 /tmp/pull-one.log
  fi
done

echo '----- local images -----'
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
