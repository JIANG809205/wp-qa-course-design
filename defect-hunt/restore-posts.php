<?php
/** 还原被权限测试改过标题的文章（OP2 会把他人文章标题改成 try-edit） */

require '/var/www/html/wp-load.php';
global $wpdb;

$rows = $wpdb->get_results("SELECT ID, post_title, post_content FROM {$wpdb->posts}
                            WHERE post_type='post' AND post_title IN ('try-edit','perm-author','perm-admin')");

foreach ($rows as $r) {
    // 从正文里恢复编号；正文形如“这是第 993 篇用于性能与分页测试的文章。”
    $title = '测试文章：质量保证与测试实践';
    if (preg_match('/第\s*(\d+)\s*篇/u', $r->post_content, $m)) {
        $title = "测试文章 {$m[1]}：质量保证与测试实践";
    }
    wp_update_post(['ID' => $r->ID, 'post_title' => $title]);
    printf("还原 #%d -> %s\n", $r->ID, $title);
}

// 同时修复被测试改过的固定链接（slug 变为 try-edit）
$slugs = $wpdb->get_results("SELECT ID, post_name FROM {$wpdb->posts}
                             WHERE post_type='post' AND post_name IN ('try-edit','perm-author','perm-admin')");
foreach ($slugs as $s) {
    $title = get_the_title($s->ID);
    $new_slug = sanitize_title($title);
    $wpdb->update($wpdb->posts, ['post_name' => $new_slug], ['ID' => $s->ID]);
    printf("修复 slug #%d -> %s\n", $s->ID, $new_slug);
}

printf("\n剩余异常标题: %d\n", (int)$wpdb->get_var(
    "SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='post'
     AND (post_title LIKE 'perm-%' OR post_title IN ('try-edit'))"));
printf("publish 文章: %d\n", (int)wp_count_posts('post')->publish);
