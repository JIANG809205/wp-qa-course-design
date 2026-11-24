#!/bin/bash
# 用 WP-CLI 清理测试残留（草稿、测试文章、测试附件），全部以 www-data 身份执行
set -u

WP="docker exec -u www-data wp-app wp"

echo "===== 1. 清理前 ====="
echo "publish: $($WP post list --post_type=post --post_status=publish --format=count)"
echo "draft  : $($WP post list --post_type=post --post_status=draft --format=count)"
echo "pending: $($WP post list --post_type=post --post_status=pending --format=count)"
echo "附件   : $($WP post list --post_type=attachment --format=count)"

echo
echo "===== 2. 删除测试草稿与待审文章 ====="
for status in draft pending; do
  ids=$($WP post list --post_type=post --post_status="$status" --format=ids)
  for id in $ids; do
    $WP post delete "$id" --force >/dev/null 2>&1 && echo "  删除 $status #$id"
  done
done

echo
echo "===== 3. 删除测试附件（文件名含 perm/测试图片）====="
att_ids=$($WP post list --post_type=attachment --format=ids)
for id in $att_ids; do
  url=$($WP post get "$id" --field=guid 2>/dev/null || echo "")
  case "$url" in
    *perm*|*%e6%b5%8b*|*测试*) $WP post delete "$id" --force >/dev/null 2>&1 && echo "  删除附件 #$id" ;;
  esac
done

echo
echo "===== 4. 清理后 ====="
echo "publish: $($WP post list --post_type=post --post_status=publish --format=count)"
echo "draft  : $($WP post list --post_type=post --post_status=draft --format=count)"
echo "pending: $($WP post list --post_type=post --post_status=pending --format=count)"
echo "附件   : $($WP post list --post_type=attachment --format=count)"
echo "用户   : $($WP user list --field=user_login --format=csv | tr '\n' ' ')"
echo "标题   : $($WP option get blogname)"
