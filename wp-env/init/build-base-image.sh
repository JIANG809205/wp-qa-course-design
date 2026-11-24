#!/bin/bash
# 本地构建基础镜像：debootstrap 生成 rootfs → docker import
set -u
export DEBIAN_FRONTEND=noninteractive

echo "===== 1. 安装 debootstrap ====="
apt-get install -y debootstrap >/tmp/deb.log 2>&1
echo "exit=$?  $(debootstrap --version 2>&1 | head -1)"

echo
echo "===== 2. debootstrap jammy（阿里云源）====="
if [ -d /opt/rootfs/etc ]; then
  echo "rootfs 已存在，跳过"
else
  rm -rf /opt/rootfs
  timeout 1200 debootstrap --variant=minbase \
    --include=ca-certificates,locales,curl,gnupg \
    jammy /opt/rootfs http://mirrors.aliyun.com/ubuntu >/tmp/debootstrap.log 2>&1
  echo "debootstrap_exit=$?"
  tail -3 /tmp/debootstrap.log
fi
du -sh /opt/rootfs 2>/dev/null

echo
echo "===== 3. 导入为 docker 镜像 ====="
if docker image inspect ubuntu:jammy-local >/dev/null 2>&1; then
  echo "镜像已存在"
else
  tar -C /opt/rootfs -c . | docker import - ubuntu:jammy-local >/tmp/import.log 2>&1
  echo "import_exit=$?"
fi

echo
echo "===== 4. 验证 ====="
docker run --rm --network host ubuntu:jammy-local bash -c 'cat /etc/os-release | head -2; echo CONTAINER_OK'
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
