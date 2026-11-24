#!/bin/bash
# 批量测试镜像加速站，找出可用的一个
set -u
IMG="library/alpine:3.20"
OK=""

for m in hub.rat.dev docker.1ms.run docker.m.daocloud.io docker.xuanyuan.me \
         docker.1panel.live docker.rainbond.cc docker.kubesre.xyz dockerpull.org \
         docker.chenby.cn dockerproxy.net; do
  printf '%-28s ' "$m"
  if timeout 40 docker pull "$m/$IMG" >/tmp/m.log 2>&1; then
    echo "OK"
    OK="$m"
    break
  else
    echo "FAIL  $(tail -1 /tmp/m.log | cut -c1-90)"
  fi
done

echo
if [ -n "$OK" ]; then
  echo "WINNER=$OK"
  echo "已写入 /etc/docker/daemon.json 作为默认加速源"
  cat >/etc/docker/daemon.json <<JSON
{
  "registry-mirrors": ["https://$OK"],
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON
else
  echo "ALL_FAILED"
fi
