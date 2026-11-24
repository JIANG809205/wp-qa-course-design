#!/bin/bash
# 重建 wordpress 镜像（固化 Apache 配置）并验证；同时检查工具链
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
SRC="$APP/local/wordpress"
BUILD=/opt/build/wordpress
COMPOSE="$APP/local/docker-compose.local.yml"

echo "===== 1. 重建 qa/wordpress ====="
mkdir -p "$BUILD"
cp "$SRC/Dockerfile" "$SRC/init.sh" "$BUILD/"
cd "$BUILD"
timeout 1800 docker build -t qa/wordpress:7.1.5 . 2>&1 | tail -4

echo
echo "===== 2. 重建 wordpress 容器（保留数据卷）====="
cd "$APP/local"
docker compose -f "$COMPOSE" rm -sf wordpress >/dev/null 2>&1 || true
docker compose -f "$COMPOSE" up -d wordpress 2>&1 | tail -2
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" = "200" ] && break
  sleep 3
done

echo
echo "===== 3. 验证（全新容器 + 原数据卷）====="
for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
  printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080$u")"
done
docker exec wp-app php -r 'define("WP_USE_THEMES",false); require "/var/www/html/wp-load.php"; global $wpdb; printf("WP %s | 文章 %s | 评论 %s | 用户 %s\n", get_bloginfo("version"), wp_count_posts("post")->publish, $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"), count_users()["total_users"]);' 2>&1 | tail -1

echo
echo "===== 4. 工具链自检 ====="
for c in java mvn jmeter google-chrome chromedriver node npm newman nikto sqlmap; do
  printf '%-16s ' "$c"
  if command -v "$c" >/dev/null 2>&1; then
    case "$c" in
      java) java -version 2>&1 | head -1 ;;
      mvn) mvn -v 2>/dev/null | head -1 ;;
      jmeter) echo "/opt/apache-jmeter-5.6.3 (非GUI可运行)" ;;
      *) echo "$(command -v $c)" ;;
    esac
  else
    echo "MISSING"
  fi
done
/opt/qa-venv/bin/python -c "import selenium,pytest,requests; print('python:', selenium.__version__, pytest.__version__, requests.__version__)" 2>/dev/null || echo "python venv 缺失"
