#!/bin/bash
# 本地构建 MariaDB 与 WordPress 镜像（基于 ubuntu:jammy-local + 阿里云 apt）
set -u

SRC="/mnt/e/软件质量保证与测试课程设计/wp-env/local"
BUILD=/opt/build
rm -rf "$BUILD"
mkdir -p "$BUILD/mariadb" "$BUILD/wordpress"
cp "$SRC/mariadb/Dockerfile" "$SRC/mariadb/entrypoint.sh" "$BUILD/mariadb/"
cp "$SRC/wordpress/Dockerfile" "$SRC/wordpress/init.sh" "$BUILD/wordpress/"

if ! docker info >/dev/null 2>&1; then
  echo "!! dockerd 未运行"
  exit 1
fi

echo "===== 构建 qa/mariadb:10.6 ====="
timeout 1800 docker build -t qa/mariadb:10.6 "$BUILD/mariadb" 2>&1 | tail -6
echo "rc=${PIPESTATUS[0]}"

echo
echo "===== 构建 qa/wordpress:7.1.5 ====="
timeout 1800 docker build -t qa/wordpress:7.1.5 "$BUILD/wordpress" 2>&1 | tail -8
echo "rc=${PIPESTATUS[0]}"

echo
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}' | grep -E 'qa/|ubuntu:jammy-local|redis'
