<?php
require '/var/www/html/wp-load.php';
global $wpdb;
$posts = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='post' AND (post_title LIKE 'perm-%' OR post_content='x' OR post_title LIKE 'qa-%')");
foreach ($posts as $id) { wp_delete_post((int)$id, true); }
echo "删除文章: ", count($posts), "\n";
$cs = $wpdb->get_col("SELECT comment_ID FROM {$wpdb->comments} WHERE comment_content LIKE 'qa-%' OR comment_content LIKE '%qa-approve%' OR comment_author='qa'");
foreach ($cs as $id) { wp_delete_comment((int)$id, true); }
echo "删除评论: ", count($cs), "\n";
echo "文章: ", (int)wp_count_posts('post')->publish, "\n";
echo "评论: ", (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"), "\n";
echo "用户: ", count_users()['total_users'], "\n";