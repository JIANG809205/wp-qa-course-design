<?php
/**
 * Plugin Name: QA Hardening
 * Description: 针对本次测试发现的配置类缺陷做最小化加固（DEF-001/002/003/004/005/006/008/009/010）。
 *              仅用于测试环境，演示"缺陷—修复—复测"闭环。
 */

if (!defined('ABSPATH')) {
    exit;
}

/* ---------- DEF-005：关闭 XML-RPC，并移除 X-Pingback 头 ---------- */
add_filter('xmlrpc_enabled', '__return_false');
add_filter('wp_headers', function ($headers) {
    unset($headers['X-Pingback']);
    return $headers;
});

/* ---------- DEF-006：未登录不得枚举 REST 用户 ---------- */
add_filter('rest_endpoints', function ($endpoints) {
    if (!is_user_logged_in()) {
        foreach (['/wp/v2/users', '/wp/v2/users/(?P<id>[\d]+)'] as $route) {
            unset($endpoints[$route]);
        }
    }
    return $endpoints;
});

/* ---------- DEF-001：登录失败限流（同一 IP 10 分钟内 5 次） ---------- */
function qa_client_key(): string
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    return 'qa_fail_' . md5($ip);
}

add_action('login_form_login', function () {
    $n = (int) get_transient(qa_client_key());
    if ($n >= 5) {
        status_header(429);
        wp_die('尝试次数过多，请 10 分钟后再试。', 'Too Many Requests', ['response' => 429]);
    }
});

add_action('wp_login_failed', function () {
    $key = qa_client_key();
    $n = (int) get_transient($key);
    set_transient($key, $n + 1, 600);
});

add_action('wp_login', function () {
    delete_transient(qa_client_key());
});

/* ---------- DEF-012：未登录不得通过 ?author=N 枚举作者 ---------- */
add_action('template_redirect', function () {
    if (is_user_logged_in()) {
        return;
    }
    if (is_author() || isset($_GET['author'])) {
        global $wp_query;
        $wp_query->set_404();
        status_header(404);
        nocache_headers();
        include get_404_template();
        exit;
    }
}, 1);

/* ---------- DEF-008：空文件上传返回 400 而不是 500 ---------- */
add_filter('rest_pre_dispatch', function ($result, $server, $request) {
    if ($request->get_method() === 'POST' && $request->get_route() === '/wp/v2/media') {
        $files = $request->get_file_params();
        if (isset($files['file']['size']) && (int) $files['file']['size'] === 0) {
            return new WP_Error('rest_upload_no_data', '文件为空，请重新选择。', ['status' => 400]);
        }
    }
    return $result;
}, 10, 3);

/* ---------- DEF-009：超出 PHP 限制时给出明确的可读提示 ---------- */
add_filter('wp_handle_upload_prefilter', function ($file) {
    if (!empty($file['error']) && (int) $file['error'] === UPLOAD_ERR_INI_SIZE) {
        $file['error'] = '文件超过服务器上传上限（upload_max_filesize），请压缩后再传。';
    }
    return $file;
});

/* ---------- DEF-011：重复用户名返回 400 而不是 500 ---------- */
add_filter('rest_pre_dispatch', function ($result, $server, $request) {
    if ($request->get_method() !== 'POST' || $request->get_route() !== '/wp/v2/users') {
        return $result;
    }
    $login = (string) $request['username'];
    if ($login !== '' && username_exists($login)) {
        return new WP_Error('existing_user_login', '该用户名已存在。', ['status' => 400]);
    }
    return $result;
}, 10, 3);
