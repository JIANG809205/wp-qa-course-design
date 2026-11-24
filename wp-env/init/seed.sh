#!/bin/sh
# WordPress 测试环境初始化脚本
# 在 wpcli 容器内执行：docker compose run --rm --entrypoint sh wpcli /init/seed.sh
set -eu

: "${SITE_URL:=http://localhost:8080}"
: "${SITE_TITLE:=WP-QA-Lab}"
: "${ADMIN_USER:=admin}"
: "${ADMIN_PASS:=Admin@2026}"
: "${ADMIN_EMAIL:=admin@example.com}"
: "${POST_COUNT:=1000}"
: "${COMMENT_COUNT:=20000}"

echo "==> [1/9] 等待数据库就绪"
i=0
until wp db check >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -gt 60 ]; then
    echo "!! 数据库连接超时，请检查 db 容器状态与 .env 凭据" >&2
    exit 1
  fi
  sleep 2
done

echo "==> [2/9] 安装 WordPress 核心"
if wp core is-installed >/dev/null 2>&1; then
  echo "    已安装，跳过（版本 $(wp core version)）"
else
  wp core install \
    --url="$SITE_URL" \
    --title="$SITE_TITLE" \
    --admin_user="$ADMIN_USER" \
    --admin_password="$ADMIN_PASS" \
    --admin_email="$ADMIN_EMAIL" \
    --skip-email
fi

echo "==> [3/9] 基础配置（时区、固定链接、评论策略）"
wp option update timezone_string 'Asia/Shanghai'
wp option update blogdescription 'Software Quality Assurance & Testing Lab'
wp rewrite structure '/%postname%/' --hard >/dev/null
# 评论必须经人工审核（对应 TC-COMM-001/002 的状态迁移）
wp option update default_comment_status open
wp option update comment_moderation 1
wp option update comment_previously_approved 0
wp option update require_name_email 1

echo "==> [4/9] 创建 5 种角色账号（权限矩阵用）"
ensure_user() {
  role="$1"; login="$2"; email="$3"; pass="$4"; name="$5"
  if wp user get "$login" >/dev/null 2>&1; then
    echo "    $login 已存在，重置角色为 $role"
    wp user set-role "$login" "$role"
    wp user update "$login" --user_pass="$pass" >/dev/null
  else
    wp user create "$login" "$email" --role="$role" --user_pass="$pass" --display_name="$name"
  fi
}
ensure_user editor      editor      editor@example.com      Editor@2026      "内容编辑"
ensure_user author      author      author@example.com      Author@2026      "作者甲"
ensure_user contributor contributor contributor@example.com Contributor@2026 "投稿者"
ensure_user subscriber  subscriber  subscriber@example.com  Subscriber@2026  "订阅者"

echo "==> [5/9] 创建示例文章"
if wp post list --post_type=post --format=count | grep -qx '0'; then
  wp post create --post_title='测试文章：欢迎来到 WP-QA-Lab' \
    --post_content='用于手工冒烟测试的示例文章。' \
    --post_status=publish --post_author=1 --porcelain >/dev/null
fi

echo "==> [6/9] 批量生成文章 ${POST_COUNT} 篇"
have_posts=$(wp post list --post_type=post --post_status=any --format=count)
if [ "$have_posts" -lt "$POST_COUNT" ]; then
  need=$((POST_COUNT - have_posts))
  wp post generate --count="$need" --post_type=post --post_status=publish >/dev/null
else
  echo "    已有 ${have_posts} 篇，跳过"
fi

echo "==> [7/9] 批量生成评论 ${COMMENT_COUNT} 条（较慢，请耐心等待）"
have_comments=$(wp comment list --format=count)
if [ "$have_comments" -lt "$COMMENT_COUNT" ]; then
  need=$((COMMENT_COUNT - have_comments))
  wp comment generate --count="$need" >/dev/null
else
  echo "    已有 ${have_comments} 条，跳过"
fi

echo "==> [8/9] 安装并启用 Redis Object Cache 插件"
if wp plugin is-installed redis-cache >/dev/null 2>&1; then
  wp plugin activate redis-cache >/dev/null || true
else
  if [ -f /init/redis-cache.zip ]; then
    wp plugin install /init/redis-cache.zip --activate >/dev/null
  else
    wp plugin install redis-cache --activate >/dev/null 2>&1 || \
      echo "    !! 插件下载失败（离线环境）：请把 redis-cache.zip 放入 init/ 后重跑本脚本"
  fi
fi
wp redis enable >/dev/null 2>&1 || true

echo "==> [9/9] 生成接口测试用应用密码"
if wp user application-password list author --format=count 2>/dev/null | grep -qx '0'; then
  APP_PASS=$(wp user application-password create author ci-runner --porcelain)
  echo "    author 的应用密码（请立即保存，只显示一次）：${APP_PASS}"
else
  echo "    author 已有应用密码，如需重建请先执行："
  echo "    wp user application-password delete author <uuid>"
fi

echo ""
echo "================ 初始化完成 ================"
printf "%-14s %s\n" "站点地址:" "$(wp option get siteurl)"
printf "%-14s %s\n" "WordPress:" "$(wp core version)"
printf "%-14s %s\n" "文章数:" "$(wp post list --post_type=post --post_status=any --format=count)"
printf "%-14s %s\n" "评论数:" "$(wp comment list --format=count)"
printf "%-14s %s\n" "插件:" "$(wp plugin list --field=name --format=csv | tr '\n' ' ')"
echo "账号：admin / editor / author / contributor / subscriber"
echo "==========================================="
