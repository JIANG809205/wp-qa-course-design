#!/bin/bash
# 为 5 个角色创建应用密码，供接口自动化使用
set -u
WP="docker exec -u www-data wp-app wp"
OUT=/tmp/wp_pass
mkdir -p "$OUT"

for role in admin editor author contributor subscriber; do
  pw=$($WP user application-password create "$role" ci-$role --porcelain 2>/dev/null)
  if [ -z "$pw" ]; then
    # 已存在则重建
    for u in $($WP user application-password list "$role" --field=uuid --format=csv 2>/dev/null); do
      $WP user application-password delete "$role" "$u" >/dev/null 2>&1
    done
    pw=$($WP user application-password create "$role" ci-$role --porcelain 2>/dev/null)
  fi
  if [ -n "$pw" ]; then
    printf '%s' "$pw" > "$OUT/$role.txt"
    echo "$role: 已生成（长度 ${#pw}）"
  else
    echo "$role: 失败"
  fi
done

echo
echo "===== 验证各角色鉴权 ====="
for role in admin editor author contributor subscriber; do
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -u "$role:$(cat "$OUT/$role.txt")" \
    http://127.0.0.1:8080/wp-json/wp/v2/users/me)
  echo "  $role -> HTTP $code"
done
