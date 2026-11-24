#!/bin/bash
# 启动 dockerd：适配缺少 bridge/iptables 模块的自定义 WSL 内核
set -u

mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{
  "registry-mirrors": ["https://hub.rat.dev"],
  "iptables": false,
  "ip6tables": false,
  "bridge": "none",
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON

pkill -9 dockerd 2>/dev/null
sleep 2
rm -f /var/run/docker.pid

nohup dockerd >/var/log/dockerd.log 2>&1 &
for i in $(seq 1 30); do
  sleep 2
  if docker info >/dev/null 2>&1; then
    echo "dockerd ready after $((i * 2))s"
    break
  fi
done
docker info --format 'server={{.ServerVersion}} driver={{.Driver}} cgroup={{.CgroupVersion}} mem={{.MemTotal}}' 2>&1
