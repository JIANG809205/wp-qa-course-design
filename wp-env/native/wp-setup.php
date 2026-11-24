<?php
/**
 * WordPress 安装 + 测试数据构造（CLI 方式，无需网页安装向导）
 * 用法：php wp-setup.php <siteUrl> <siteTitle> <adminUser> <adminPass> <adminEmail>
 */

$siteUrl    = $argv[1] ?? 'http://localhost:8080';
$siteTitle  = $argv[2] ?? 'WP-QA-Lab';
$adminUser  = $argv[3] ?? 'admin';
$adminPass  = $argv[4] ?? 'Admin@2026';
$adminEmail = $argv[5] ?? 'admin@example.com';

define('WP_INSTALLING', true);
require '/var/www/html/wp-load.php';
require ABSPATH . 'wp-admin/includes/upgrade.php';

if (!is_blog_installed()) {
    wp_install($siteTitle, $adminUser, $adminEmail, true, '', $adminPass);
    echo "[install] 核心安装完成\n";
} else {
    echo "[install] 已安装，跳过\n";
}

// ---- 基础配置 ----
update_option('siteurl', $siteUrl);
update_option('home', $siteUrl);
update_option('blogname', $siteTitle);
update_option('blogdescription', 'Software Quality Assurance & Testing Lab');
update_option('timezone_string', 'Asia/Shanghai');
update_option('permalink_structure', '/%postname%/');
// 评论必须人工审核：对应 TC-COMM-001/002 的状态迁移
update_option('default_comment_status', 'open');
update_option('comment_moderation', 1);
update_option('comment_previously_approved', 0);
update_option('require_name_email', 1);
echo "[config] 站点地址/时区/固定链接/评论策略 已设置\n";

// ---- 5 个角色账号 ----
$users = [
    'editor'      => ['editor@example.com',      'Editor@2026',      '内容编辑', 'editor'],
    'author'      => ['author@example.com',      'Author@2026',      '作者甲',   'author'],
    'contributor' => ['contributor@example.com', 'Contributor@2026', '投稿者',   'contributor'],
    'subscriber'  => ['subscriber@example.com',  'Subscriber@2026',  '订阅者',   'subscriber'],
];

foreach ($users as $login => $info) {
    [$email, $pass, $display, $role] = $info;
    $existing = get_user_by('login', $login);
    if ($existing) {
        $uid = $existing->ID;
        wp_set_password($pass, $uid);
    } else {
        $uid = wp_create_user($login, $pass, $email);
        if (is_wp_error($uid)) {
            echo "[user] {$login} 创建失败: " . $uid->get_error_message() . "\n";
            continue;
        }
    }
    $u = new WP_User($uid);
    $u->set_role($role);
    wp_update_user(['ID' => $uid, 'display_name' => $display]);
    echo "[user] {$login} ({$role}) 就绪\n";
}

// ---- 文章 ----
$postTarget = (int)(getenv('POST_COUNT') ?: 1000);
$counts = wp_count_posts('post');
$have = (int)$counts->publish;
if ($have < $postTarget) {
    for ($i = $have + 1; $i <= $postTarget; $i++) {
        wp_insert_post([
            'post_title'   => "测试文章 {$i}：质量保证与测试实践",
            'post_content' => "这是第 {$i} 篇用于性能与分页测试的文章。\n\n关键词：软件测试、质量保证、自动化。",
            'post_status'  => 'publish',
            'post_author'  => 1,
            'post_type'    => 'post',
        ]);
        if ($i % 200 === 0) {
            echo "[post] 已生成 {$i}/{$postTarget}\n";
        }
    }
}
echo "[post] 当前已发布文章数：" . wp_count_posts('post')->publish . "\n";

// ---- 评论（批量 SQL，快于逐条 wp_insert_comment）----
global $wpdb;
$commentTarget = (int)(getenv('COMMENT_COUNT') ?: 20000);
$have_comments = (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}");
if ($have_comments < $commentTarget) {
    $ids = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_status='publish' AND post_type='post' LIMIT 50");
    if (empty($ids)) {
        echo "[comment] 没有可用文章，跳过\n";
    } else {
        $batch = 500;
        $done = $have_comments;
        while ($done < $commentTarget) {
            $n = min($batch, $commentTarget - $done);
            $values = [];
            for ($i = 0; $i < $n; $i++) {
                $pid = $ids[array_rand($ids)];
                $values[] = $wpdb->prepare(
                    "(%d, %s, %s, %s, %s, %s, '1', 'comment')",
                    $pid,
                    '访客' . ($done + $i),
                    'guest' . ($done + $i) . '@example.com',
                    '这是一条用于列表与性能测试的评论。',
                    current_time('mysql'),
                    current_time('mysql')
                );
            }
            $sql = "INSERT INTO {$wpdb->comments}
                    (comment_post_ID, comment_author, comment_author_email, comment_content,
                     comment_date, comment_date_gmt, comment_approved, comment_type)
                    VALUES " . implode(',', $values);
            $wpdb->query($sql);
            $done += $n;
            if ($done % 5000 < 500) {
                echo "[comment] 已生成 {$done}/{$commentTarget}\n";
            }
        }
        // 修正评论计数
        $wpdb->query("UPDATE {$wpdb->posts} p SET comment_count = (
            SELECT COUNT(*) FROM {$wpdb->comments} c
            WHERE c.comment_post_ID = p.ID AND c.comment_approved = '1')");
        echo "[comment] 完成，总计：" . $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}") . "\n";
    }
} else {
    echo "[comment] 已有 {$have_comments} 条，跳过\n";
}

// ---- 接口测试用应用密码 ----
$author = get_user_by('login', 'author');
if ($author && class_exists('WP_Application_Passwords')) {
    $passwords = WP_Application_Passwords::get_user_application_passwords($author->ID);
    if (empty($passwords)) {
        $created = WP_Application_Passwords::create_new_application_password($author->ID, ['name' => 'ci-runner']);
        if (!is_wp_error($created)) {
            echo "\n[app-password] author 的应用密码（只显示一次，请保存）：\n    {$created[0]}\n\n";
        } else {
            echo "[app-password] 创建失败: " . $created->get_error_message() . "\n";
        }
    } else {
        echo "[app-password] author 已有应用密码，如需重建请删除后重跑\n";
    }
}

echo "\n================ 初始化结果 ================\n";
printf("%-14s %s\n", '站点地址:', get_option('siteurl'));
printf("%-14s %s\n", 'WordPress:', get_bloginfo('version'));
printf("%-14s %s\n", '文章数:', wp_count_posts('post')->publish);
printf("%-14s %s\n", '评论数:', $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments}"));
printf("%-14s %s\n", '固定链接:', get_option('permalink_structure'));
printf("%-14s %s\n", '评论审核:', get_option('comment_moderation') ? '开启' : '关闭');
echo "==========================================\n";
