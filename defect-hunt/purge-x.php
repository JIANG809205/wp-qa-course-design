<?php
require '/var/www/html/wp-load.php';
global $wpdb;
$ids = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='post' AND post_content='x'");
foreach ($ids as $id) { wp_delete_post((int)$id, true); printf("删除测试文章 #%d\n", $id); }
printf("publish 文章: %d\n", (int)wp_count_posts('post')->publish);
printf("残留 content=x: %d\n", (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='post' AND post_content='x'"));