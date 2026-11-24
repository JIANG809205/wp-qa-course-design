<?php
/**
 * 清理权限矩阵等测试产生的脏数据，并恢复站点配置。
 * 在容器内执行：php /tmp/cleanup.php
 */

require '/var/www/html/wp-load.php';

global $wpdb;

echo "=== 清理前 ===\n";
printf("站点标题: %s\n", get_option('blogname'));
printf("文章总数: %d\n", (int)wp_count_posts('post')->publish);
printf("用户总数: %d\n", count_users()['total_users']);

// 1) 删除测试期间创建的文章（标题以 perm- 开头）
$posts = $wpdb->get_col("SELECT ID FROM {$wpdb->posts}
                         WHERE post_type='post' AND post_title LIKE 'perm-%'");
foreach ($posts as $pid) {
    wp_delete_post((int)$pid, true);
}
printf("删除测试文章: %d 篇\n", count($posts));

// 2) 删除测试期间上传的附件
$atts = $wpdb->get_col("SELECT ID FROM {$wpdb->posts}
                        WHERE post_type='attachment' AND guid LIKE '%perm-%'");
foreach ($atts as $aid) {
    wp_delete_attachment((int)$aid, true);
}
printf("删除测试附件: %d 个\n", count($atts));

// 3) 删除测试期间创建的用户（内容转交给 admin）
require_once ABSPATH . 'wp-admin/includes/user.php';
$test_users = $wpdb->get_col("SELECT ID FROM {$wpdb->users}
    WHERE user_login LIKE 'perm\_%' ESCAPE '\\\\'
       OR user_login LIKE 'perm2\_%' ESCAPE '\\\\'
       OR user_login IN ('dup_probe','hacker01','perm_probe_admin')");
foreach ($test_users as $uid) {
    if ((int)$uid === 1) {
        continue;
    }
    wp_delete_user((int)$uid, 1);
}
printf("删除测试用户: %d 个\n", count($test_users));

// 4) 恢复站点标题与被改动的设置
update_option('blogname', 'WP-QA-Lab');
update_option('blogdescription', 'Software Quality Assurance & Testing Lab');
printf("站点标题已恢复: %s\n", get_option('blogname'));

// 5) 清理残留的待审评论（测试提交的“自动化评论/自动化XSS测试”）
$comments = $wpdb->get_col("SELECT comment_ID FROM {$wpdb->comments}
    WHERE comment_content LIKE '%自动化评论-%' OR comment_content LIKE '%自动化XSS测试%'");
foreach ($comments as $cid) {
    wp_delete_comment((int)$cid, true);
}
printf("删除测试评论: %d 条\n", count($comments));

echo "\n=== 清理后 ===\n";
printf("站点标题: %s\n", get_option('blogname'));
printf("文章总数: %d\n", (int)wp_count_posts('post')->publish);
printf("用户总数: %d\n", count_users()['total_users']);
printf("评论总数: %d\n", (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"));
