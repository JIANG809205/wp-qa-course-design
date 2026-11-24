#!/bin/bash
# 逐个测试镜像加速站是否可用
for m in docker.1ms.run dockerproxy.net hub.rat.dev docker.m.daocloud.io mirror.ccs.tencentyun.com docker.xuanyuan.me; do
  printf '== %-32s : ' "$m"
  if timeout 45 docker pull "$m/library/alpine:3.20" >/tmp/pull.log 2>&1; then
    echo OK
    break
  else
    echo FAIL
    tail -1 /tmp/pull.log
  fi
done
echo '----- images -----'
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}'
