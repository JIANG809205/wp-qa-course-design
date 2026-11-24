<?php
/**
 * Plugin Name: QA Environment Tweaks
 * Description: 课程设计测试环境固定项。
 */

// 1) 统一使用经典编辑器，保证自动化选择器稳定（区块编辑器没有 #title）
add_filter('use_block_editor_for_post_type', '__return_false', 100);
add_filter('use_block_editor_for_post', '__return_false', 100);

// 2) 关闭新用户欢迎弹窗，避免遮挡元素
remove_action('admin_init', 'wp_welcome_panel');

// 3) 首页固定每页文章数，便于脚本定位
add_filter('pre_option_posts_per_page', function () {
    return 10;
});

// 4) 测试环境关闭评论洪水保护：用例会连续提交评论，生产环境应保留此项
add_action('init', function () {
    remove_action('check_comment_flood', 'check_comment_flood_db', 10);
}, 20);
