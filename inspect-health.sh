#!/bin/bash
# 只读体检：Redis 是否真被 WordPress 使用；工具链声明核实
set -u
echo "== WordPress 侧 =="
echo -n "WP_CACHE=";        docker exec wp-app wp config get WP_CACHE --allow-root 2>&1
echo -n "drop-in 插件: ";   docker exec wp-app wp plugin list --status=dropin --field=name --allow-root 2>&1 | tr '\n' ' '; echo
echo -n "已启用插件: ";     docker exec wp-app wp plugin list --status=active --field=name --allow-root 2>&1 | tr '\n' ' '; echo
echo -n "wp-content 下 drop-in 文件: "
docker exec wp-app sh -c 'ls /var/www/html/wp-content/ | grep -E "object-cache|advanced-cache" || echo 无'
echo "== Redis 侧 =="
echo -n "redis 键总数: "; docker exec wp-redis redis-cli dbsize
echo -n "redis 已用内存: "; docker exec wp-redis redis-cli info memory | grep used_memory_human
echo -n "redis 累计命令数: "; docker exec wp-redis redis-cli info stats | grep total_commands_processed
echo "== 访问一次首页后再看 =="
curl -sL -o /dev/null http://localhost:8080/
echo -n "redis 键总数: "; docker exec wp-redis redis-cli dbsize
echo "== 工具是否存在 =="
for t in nikto sqlmap newman wpscan zap.sh; do printf '%-8s ' "$t"; command -v $t || echo 未安装; done
