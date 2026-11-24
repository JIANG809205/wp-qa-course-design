#!/bin/bash
# 核对官方发布包与中文包的差异，并检查当前站点状态
set -u

echo "===== 1. 官方发布包可达性 ====="
for u in \
  "https://wordpress.org/wordpress-7.1.5.tar.gz" \
  "https://wordpress.org/wordpress-7.1.5.zip" \
  "https://wordpress.org/download/releases/7.1/" ; do
  printf '%-58s ' "$u"
  curl -s -o /dev/null -m 25 -w '%{http_code}\n' -L "$u" 2>/dev/null
done

echo
echo "===== 2. 下载官方发布包 ====="
if [ ! -s /tmp/wp-official-7.1.5.tar.gz ]; then
  curl -fsSL -m 300 -o /tmp/wp-official-7.1.5.tar.gz "https://wordpress.org/wordpress-7.1.5.tar.gz" \
    && echo "下载完成 $(du -h /tmp/wp-official-7.1.5.tar.gz | cut -f1)" \
    || { echo "下载失败"; exit 1; }
fi
rm -rf /tmp/wp-official && mkdir -p /tmp/wp-official
tar xzf /tmp/wp-official-7.1.5.tar.gz -C /tmp/wp-official

echo
echo "===== 3. 与容器内（中文包）逐文件比对核心文件 ====="
for f in wp-includes/version.php wp-admin/admin.php wp-login.php wp-settings.php wp-includes/default-filters.php; do
  a=$(md5sum "/tmp/wp-official/wordpress/$f" 2>/dev/null | awk '{print $1}')
  b=$(docker exec wp-app md5sum "/var/www/html/$f" 2>/dev/null | awk '{print $1}')
  if [ "$a" = "$b" ]; then s="一致"; else s="不同"; fi
  printf '  %-32s 官方=%s 容器=%s  %s\n' "$f" "${a:0:8}" "${b:0:8}" "$s"
done

echo
echo "===== 4. 版本与语言 ====="
docker exec -u www-data wp-app wp core version 2>/dev/null
docker exec -u www-data wp-app wp option get WPLANG 2>/dev/null || echo "WPLANG 未设置"
docker exec -u www-data wp-app wp language core list --status=active 2>/dev/null | head -3

echo
echo "===== 5. 当前站点状态（首页是否已设为静态页）====="
docker exec -u www-data wp-app wp option get show_on_front 2>/dev/null
docker exec -u www-data wp-app wp option get page_on_front 2>/dev/null
echo "HTTP: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/)"
