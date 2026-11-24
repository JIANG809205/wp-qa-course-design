#!/bin/bash
# Docker 测试栈控制：start | stop | restart | status | reset
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
COMPOSE="$APP/local/docker-compose.local.yml"

ensure_docker() {
  if docker info >/dev/null 2>&1; then return 0; fi
  pkill -9 dockerd 2>/dev/null
  sleep 2
  rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 30); do sleep 2; docker info >/dev/null 2>&1 && return 0; done
  return 1
}

ensure_keepalive() {
  pgrep -f dsh-wp-keepalive >/dev/null 2>&1 || \
    setsid nohup bash -c 'exec -a dsh-wp-keepalive sleep infinity' >/dev/null 2>&1 &
}

start_all() {
  ensure_docker || { echo "dockerd 启动失败"; return 1; }
  ensure_keepalive
  cd "$APP/local" || return 1
  docker compose -f "$COMPOSE" up -d 2>&1 | tail -4
  for i in $(seq 1 40); do
    code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
    [ "$code" = "200" ] && break
    sleep 3
  done
  echo "站点 HTTP=$code"
}

stop_all() {
  cd "$APP/local" || return 1
  docker compose -f "$COMPOSE" stop 2>&1 | tail -3
}

status_all() {
  ensure_docker || echo "(dockerd 未运行)"
  cd "$APP/local" || return 1
  docker compose -f "$COMPOSE" ps
  echo "--- HTTP ---"
  for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
    printf '  %-42s %s\n' "$u" "$(curl -s -o /dev/null -m 3 -w '%{http_code}' "http://127.0.0.1:8080$u")"
  done
  echo "--- 数据 ---"
  docker exec wp-app php -r 'define("WP_USE_THEMES",false); require "/var/www/html/wp-load.php"; global $wpdb; printf("  WP %s | 文章 %s | 评论 %s | 用户 %s\n", get_bloginfo("version"), wp_count_posts("post")->publish, $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"), count_users()["total_users"]);' 2>/dev/null
}

case "${1:-status}" in
  start)   start_all ;;
  stop)    stop_all ;;
  restart) stop_all; start_all ;;
  status)  status_all ;;
  reset)
    cd "$APP/local" || exit 1
    docker compose -f "$COMPOSE" down -v 2>&1 | tail -3
    echo "已清空容器与数据卷，重新执行 start 会重新初始化"
    ;;
  *) echo "用法: stack.sh {start|stop|restart|status|reset}" ;;
esac
