#!/bin/bash
# 标准模式启动 dockerd（官方内核，bridge + iptables 完整）
set -u

mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{
  "registry-mirrors": [
    "https://hub.rat.dev",
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io"
  ],
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON

pkill -9 dockerd 2>/dev/null
sleep 2
rm -f /var/run/docker.pid

nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
for i in $(seq 1 30); do
  sleep 2
  if docker info >/dev/null 2>&1; then
    echo "dockerd ready after $((i * 2))s"
    break
  fi
done

docker info --format 'server={{.ServerVersion}} driver={{.Driver}} cgroup={{.CgroupVersion}} mem={{.MemTotal}}'
echo "--- bridge ---"
ip -br addr show docker0 2>/dev/null || echo "no docker0"
echo "--- log tail ---"
tail -3 /var/log/dockerd.log
