#!/bin/bash
# MariaDB 容器入口：启动后幂等创建库与账号（不依赖数据目录是否已初始化）
set -e

DATADIR=/var/lib/mysql

mkdir -p /run/mysqld
chown -R mysql:mysql /run/mysqld 2>/dev/null || true
chown -R mysql:mysql "$DATADIR" 2>/dev/null || true

# 后台守护：等服务起来后幂等建库建号
(
  for i in $(seq 1 90); do
    if mariadb-admin ping >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if mariadb-admin ping >/dev/null 2>&1; then
    echo "[provision] 创建数据库与账号"
    mariadb <<SQL
CREATE DATABASE IF NOT EXISTS \`${MARIADB_DATABASE}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MARIADB_USER}'@'%' IDENTIFIED BY '${MARIADB_PASSWORD}';
ALTER USER '${MARIADB_USER}'@'%' IDENTIFIED BY '${MARIADB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${MARIADB_DATABASE}\`.* TO '${MARIADB_USER}'@'%';
FLUSH PRIVILEGES;
SQL
    echo "[provision] 完成：$(mariadb -N -e "SELECT COUNT(*) FROM mysql.user WHERE User='${MARIADB_USER}'") 个账号"
  else
    echo "[provision] 失败：数据库未能启动" >&2
  fi
) &

echo "[start] mysqld 启动（监听 0.0.0.0）"
exec mysqld_safe --datadir="$DATADIR" --bind-address=0.0.0.0 "$@"
