#!/bin/bash
# 把主实例（8080）首页整理为静态首页：访问者看到介绍页，1000 篇测试文章归入「博客」页
set -u
WP="docker exec -u www-data wp-app wp"

echo "===== 1. 创建静态首页与博客页 ====="
$WP post list --post_type=page --fields=ID,post_title --format=csv 2>/dev/null

HOME_ID=$($WP post list --post_type=page --name=qa-home --format=ids 2>/dev/null)
if [ -z "$HOME_ID" ]; then
  HOME_ID=$($WP post create --post_type=page --post_status=publish --post_title="WP-QA-Lab 测试环境" \
    --post_name=qa-home --porcelain \
    --post_content='<h2>这是一个软件测试实验环境</h2>
<p>本站是用官方 WordPress 7.1.5 简体中文版部署的被测系统，用于《软件质量保证与测试》课程设计。</p>
<ul>
<li>测试对象：WordPress 7.1.5（本地 Docker 部署）</li>
<li>数据基线：1000 篇测试文章、20000 条评论、5 个角色账号</li>
<li>测试类型：功能、接口、性能、安全、兼容性</li>
<li>当前版本：已执行 40 条用例、12 条缺陷记录、30 格权限验证</li>
</ul>
<p>测试文章统一命名为「测试文章 N：质量保证与测试实践」，集中在<a href="/?page_id=' 2>/dev/null)
  echo "创建首页 #$HOME_ID"
fi

BLOG_ID=$($WP post list --post_type=page --name=qa-blog --format=ids 2>/dev/null)
if [ -z "$BLOG_ID" ]; then
  BLOG_ID=$($WP post create --post_type=page --post_status=publish --post_title="博客" --post_name=qa-blog --porcelain)
  echo "创建博客页 #$BLOG_ID"
fi

# 给首页补一个指向博客页的链接
$WP post update "$HOME_ID" --post_content="<h2>这是一个软件测试实验环境</h2>
<p>本站是用官方 WordPress 7.1.5 简体中文版部署的被测系统，用于《软件质量保证与测试》课程设计。</p>
<ul>
<li>测试对象：WordPress 7.1.5（官方发布包，本地 Docker 部署）</li>
<li>数据基线：1000 篇测试文章、20000 条评论、5 个角色账号</li>
<li>测试类型：功能、接口、性能、安全、兼容性</li>
<li>已执行：40 条用例、12 条缺陷记录、30 格权限验证、11 组压测</li>
</ul>
<p>全部测试文章见 <a href=\"/?page_id=${BLOG_ID}\">博客</a> 页面。</p>" >/dev/null 2>&1

echo
echo "===== 2. 设为静态首页 ====="
$WP option update show_on_front page
$WP option update page_on_front "$HOME_ID"
$WP option update page_for_posts "$BLOG_ID"
$WP option update blogdescription "软件质量保证与测试课程设计 · 被测环境"
$WP rewrite flush --hard >/dev/null 2>&1

echo
echo "===== 3. 复核 ====="
echo "首页设置: $($WP option get show_on_front)"
echo "首页 ID: $($WP option get page_on_front)，标题: $($WP post get "$HOME_ID" --field=post_title)"
echo "博客页 ID: $($WP option get page_for_posts)"
echo "文章总数: $($WP post list --post_type=post --post_status=publish --format=count)"
echo "HTTP: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/)"
