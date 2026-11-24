#!/bin/bash
# 安装官方 WP-CLI（经 fastly.jsdelivr 镜像），并用它验证数据构造能力
set -u

echo "===== 1. 下载 wp-cli.phar ====="
if [ -s /tmp/wp-cli.phar ]; then
  echo "已存在 $(du -h /tmp/wp-cli.phar | cut -f1)"
else
  curl -fsSL -m 180 -o /tmp/wp-cli.phar \
    "https://fastly.jsdelivr.net/gh/wp-cli/builds@gh-pages/phar/wp-cli.phar"
  echo "下载完成: $(du -h /tmp/wp-cli.phar | cut -f1)"
fi
php /tmp/wp-cli.phar --version 2>&1 | head -2

echo
echo "===== 2. 安装进容器 ====="
docker cp /tmp/wp-cli.phar wp-app:/usr/local/bin/wp
docker exec wp-app chmod +x /usr/local/bin/wp
docker exec -u www-data wp-app wp --info 2>&1 | head -8

echo
echo "===== 3. 用官方命令查看现状 ====="
docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count
docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=ids | awk '{print NF" 个 ID"}'
docker exec -u www-data wp-app wp user list --fields=user_login,roles --format=table
docker exec -u www-data wp-app wp option get blogname

echo
echo "===== 4. 验证官方数据构造命令（生成 3 篇草稿后立即删除）====="
IDS=$(docker exec -u www-data wp-app wp post generate --count=3 --post_type=post --post_status=draft --post_author=1 --format=ids)
echo "生成: $IDS"
docker exec -u www-data wp-app wp post list --post_status=draft --format=count
for id in $IDS; do
  docker exec -u www-data wp-app wp post delete "$id" --force >/dev/null 2>&1
done
echo "删除后草稿数: $(docker exec -u www-data wp-app wp post list --post_status=draft --format=count)"

echo
echo "===== 5. 结果 ====="
echo "publish 文章: $(docker exec -u www-data wp-app wp post list --post_type=post --post_status=publish --format=count)"
