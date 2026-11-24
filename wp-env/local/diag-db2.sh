#!/bin/bash
# 检查 db 镜像与运行时配置是否生效
echo "===== 镜像创建时间 ====="
docker image inspect qa/mariadb:10.6 --format '{{.Created}} {{.Id}}'

echo
echo "===== 容器内配置文件 ====="
docker exec wp-db bash -c "cat /etc/mysql/mariadb.conf.d/99-qa.cnf 2>/dev/null || echo '配置文件不存在'"

echo
echo "===== mysqld 实际生效参数 ====="
docker exec wp-db bash -c "mysqld --print-defaults 2>/dev/null | tr ' ' '\n' | grep -i bind || echo '未找到 bind-address 参数'"

echo
echo "===== 容器内 50-server.cnf 的 bind-address ====="
docker exec wp-db bash -c "grep -n 'bind-address' /etc/mysql/mariadb.conf.d/50-server.cnf 2>/dev/null || echo none"

echo
echo "===== 容器启动命令 ====="
docker inspect wp-db --format '{{.Config.Cmd}} | {{.Config.Entrypoint}}'

echo
echo "===== 手工在容器内测试端口 ====="
docker exec wp-db bash -c "timeout 3 bash -c '(echo > /dev/tcp/127.0.0.1/3306)' && echo LOCAL_OK || echo LOCAL_FAIL"
