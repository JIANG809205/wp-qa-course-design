#!/bin/bash
# 安装并启动 Redis（供对象缓存性能实验使用）
set -u
export DEBIAN_FRONTEND=noninteractive
apt-get install -y redis-server >/tmp/redis.log 2>&1
echo "apt_exit=$?"
service redis-server status >/dev/null 2>&1 || service redis-server start
sleep 2
echo "ping: $(redis-cli ping 2>&1 | head -1)"
redis-cli info server 2>/dev/null | grep -E 'redis_version|tcp_port'
