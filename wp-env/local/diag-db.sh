#!/bin/bash
# 诊断容器网络与数据库监听
set -u
echo "===== 网络 ====="
docker network ls
echo "--- 各容器所属网络 ---"
for c in wp-app wp-db wp-redis; do
  printf '%-10s ' "$c"
  docker inspect "$c" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' 2>/dev/null || echo "容器不存在"
done

echo
echo "===== DNS 解析 ====="
docker exec wp-app getent hosts db 2>&1 || echo "解析失败"

echo
echo "===== db 监听端口 ====="
docker exec wp-db bash -c "ss -lntp 2>/dev/null | grep 3306 || netstat -lntp 2>/dev/null | grep 3306 || echo '未监听 3306'"

echo
echo "===== db 日志尾部 ====="
docker logs --tail 15 wp-db 2>&1

echo
echo "===== 从 app 侧连通性 ====="
docker exec wp-app bash -c 'timeout 3 bash -c "(echo > /dev/tcp/db/3306)" && echo TCP_OK || echo TCP_FAIL'
docker exec wp-app bash -c 'php -r "\$c=@mysqli_connect(\"db\",\"wpuser\",\"wp_pass_2026\",\"wordpress\",3306); echo \$c ? \"MYSQL_OK\" : \"MYSQL_FAIL: \".mysqli_connect_error();" 2>&1'
