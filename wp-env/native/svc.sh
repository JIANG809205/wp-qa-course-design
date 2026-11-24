#!/bin/bash
# WordPress 测试环境服务控制（WSL 无 systemd）
# 注意：WSL 在没有活动进程时会回收虚拟机，导致服务停止。
# 因此 start 时会启动一个常驻 keepalive 进程，保持虚拟机存活。
set -u
PORT=8080

start_all() {
  mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
  service mariadb start >/dev/null 2>&1
  service redis-server start >/dev/null 2>&1
  service apache2 start >/dev/null 2>&1
  # 保活：防止 WSL 因空闲回收虚拟机（setsid 脱离当前会话，避免随终端退出）
  if ! pgrep -f "dsh-keepalive" >/dev/null 2>&1; then
    setsid nohup bash -c 'exec -a dsh-keepalive sleep infinity' >/dev/null 2>&1 &
    sleep 1
  fi
  sleep 3
}

stop_all() {
  service apache2 stop >/dev/null 2>&1
  service redis-server stop >/dev/null 2>&1
  service mariadb stop >/dev/null 2>&1
  pkill -f dsh-keepalive 2>/dev/null
  echo "stopped"
}

status_all() {
  echo "--- 服务 ---"
  for s in mariadb redis-server apache2; do
    if service "$s" status >/dev/null 2>&1; then echo "  $s: running"; else echo "  $s: stopped"; fi
  done
  echo "--- keepalive ---"
  pgrep -af "dsh-keepalive" | head -1 || echo "  none"
  echo "--- HTTP ---"
  for u in "/" "/wp-login.php" "/wp-json/wp/v2/posts?per_page=1" "/wp-admin/"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${PORT}${u}")
    printf '  %-40s %s\n' "$u" "$code"
  done
  echo "--- 数据 ---"
  php -r '
    define("WP_USE_THEMES", false);
    require "/var/www/html/wp-load.php";
    global $wpdb;
    printf("  WordPress: %s\n", get_bloginfo("version"));
    printf("  文章数: %s\n", wp_count_posts("post")->publish);
    printf("  评论数: %s\n", $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"));
    printf("  用户数: %s\n", count_users()["total_users"]);
  ' 2>&1 | head -6
}

case "${1:-status}" in
  start)   start_all; status_all ;;
  stop)    stop_all ;;
  restart) stop_all; start_all; status_all ;;
  status)  status_all ;;
  *) echo "用法: svc.sh {start|stop|restart|status}" ;;
esac
