# WordPress 测试环境（原生 LAMP 版）— 已在本机部署完成

> 本机实测：**已可访问、已初始化 1000 篇文章 / 20000 条评论 / 5 个角色账号**。

---

## 一、为什么不用 Docker

| 尝试 | 结果 | 原因 |
|---|---|---|
| Docker Desktop | 未安装 | — |
| WSL 内装 Docker 引擎 | ✗ | 本机 WSL 使用自定义内核 `6.6.123.2-oslab`，**缺少 bridge 模块**，`ip link add ... type bridge` 报 "Unknown device type"，dockerd 无法创建 docker0 |
| 绕过 bridge（host 网络） | 部分可行 | dockerd 能起，但**镜像源全部超时**（hub.rat.dev / docker.1ms.run / dockerproxy.net 等 TLS 握手失败），拉不动 wordpress/mariadb 镜像 |
| **原生 LAMP（采用）** | ✓ | apt 走阿里云镜像 844 KB/s，10 分钟装完；无需 bridge、无需拉镜像 |

> 结论：**本机用原生 LAMP**；`wp-env/docker-compose*.yml` 保留，换到有正常 Docker 的机器仍可用。

---

## 二、当前环境（实测）

| 组件 | 版本 |
|---|---|
| 宿主 | Windows 11 + WSL2 (Ubuntu 22.04.5 LTS, 内核 6.6.123.2-oslab) |
| Web 服务器 | Apache 2.4.52 |
| PHP | 8.1.2（mod_php） |
| 数据库 | MariaDB 10.6.23 |
| 缓存 | Redis 6.0.16 |
| 被测系统 | **WordPress 7.1.5（zh_CN）** |
| 访问地址 | <http://localhost:8080> |
| 后台 | <http://localhost:8080/wp-admin/> |

**数据基线**：文章 1000 篇、评论 20000 条、用户 5 个、固定链接 `/%postname%/`、评论必须人工审核。

---

## 三、账号

| 角色 | 用户名 | 密码 | 用途 |
|---|---|---|---|
| 管理员 | `admin` | `Admin@2026` | 正向基线 |
| 编辑 | `editor` | `Editor@2026` | 权限矩阵 OP2/OP3 正向 |
| 作者 | `author` | `Author@2026` | OP2 负向、OP4 正向 |
| 投稿者 | `contributor` | `Contributor@2026` | OP1 负向（只能提交待审） |
| 订阅者 | `subscriber` | `Subscriber@2026` | 后台访问负向 |

**接口测试应用密码**（author，只显示一次，已保存备用）：

```
N8rmt7Wj6WVO81NX3uTgWhDt
```

用法：

```bash
curl -u 'author:N8rmt7Wj6WVO81NX3uTgWhDt' http://localhost:8080/wp-json/wp/v2/users/me
```

> 应用密码在 http 下可用，是因为 wp-config.php 里加了 `define('WP_ENVIRONMENT_TYPE', 'local');`。没有这一行会返回 `rest_not_logged_in`。

---

## 四、日常操作

```powershell
cd E:\软件质量保证与测试课程设计\wp-env\native
.\control.ps1 status     # 查看服务与站点状态
.\control.ps1 start      # 启动 MariaDB / Redis / Apache（含保活进程）
.\control.ps1 stop       # 全部停止
.\control.ps1 restart    # 重启
```

> **重要**：WSL 在没有活动进程时会回收虚拟机，服务会跟着停。`start` 会拉起一个 `dsh-keepalive` 常驻进程防止回收；如果发现站点打不开，先执行 `.\control.ps1 start`。

等价的手工命令：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash /mnt/e/软件质量保证与测试课程设计/wp-env/native/svc.sh start
```

---

## 五、文件说明

| 文件 | 作用 |
|---|---|
| `native-setup.sh` | 一键部署（建库、下载 WP、解压、写配置、配 Apache、装数据） |
| `wp-setup.php` | 安装核心 + 建 5 角色 + 生成文章/评论 + 建应用密码 |
| `svc.sh` | 服务启停与状态检查（含 keepalive） |
| `control.ps1` | Windows 侧包装 |
| `fix-rewrite.sh` | 写 `.htaccess`、开 `AllowOverride`、验证 REST |
| `enable-app-password.sh` | 打开 `WP_ENVIRONMENT_TYPE=local` |
| `install-lamp.sh` / `install-redis.sh` | 依赖安装 |

关键路径：站点根目录 `/var/www/html`（WSL 内），数据库 `wordpress`，账号 `wpuser / wp_pass_2026`。

---

## 六、验证清单（已通过）

| 检查 | 结果 |
|---|---|
| 首页 | HTTP 200 |
| 登录页 | HTTP 200，含登录表单 |
| `/wp-admin/` 未登录 | HTTP 302（跳转登录，符合预期） |
| REST 文章列表 | HTTP 200，返回 JSON |
| 应用密码鉴权 | 200，返回 `作者甲` |
| 未授权创建文章 | HTTP 401（正确拒绝） |
| 未认证 `/wp-json/wp/v2/users` | 200，暴露 id/name/slug/avatar 等字段 ← **TC-API-006 的实测证据** |
| 文章数 / 评论数 / 用户数 | 1000 / 20000 / 5 |

---

## 七、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 站点打不开、`建立数据库连接时出错` | WSL 虚拟机被回收，服务已停 | `.\control.ps1 start` |
| REST 全部 404 | `.htaccess` 或 `AllowOverride` 未生效 | 重跑 `fix-rewrite.sh` |
| 接口返回 `rest_not_logged_in`（即使密码对） | 应用密码要求 HTTPS 或 local 环境 | 确认 wp-config.php 有 `WP_ENVIRONMENT_TYPE=local` |
| 上传大图失败 | PHP 上传上限 | 修改 `/etc/php/8.1/apache2/php.ini` 的 `upload_max_filesize`，重启 Apache |
| 端口 8080 被占 | 其他程序冲突 | 改 `/etc/apache2/ports.conf` 与 vhost，重启 Apache |
| 中文文件名乱码 | 未装语言包 | 后台「设置→常规→站点语言」选简体中文 |

---

## 八、下一步（安全双版本对照）

原生方式做"修复前/修复后"对照，比 Docker 更简单：

1. 下载旧版本：`wget https://cn.wordpress.org/wordpress-6.6.2-zh_CN.zip`
2. 解压到 `/var/www/html-old`，复制一份 `wp-config.php`（改库名为 `wordpress_old`）
3. 建库建用户，跑一次安装（复用 `wp-setup.php`，改路径与库名）
4. 新增 vhost 监听 8081，指向 `/var/www/html-old`
5. 对同一靶点分别请求两个端口，记录"旧版未拦截 / 新版已拦截"

> 注意：WordPress 已到 7.1.x，选对照版本时优先挑**同一大版本相邻的两个小版本**（如 7.1.4 与 7.1.5），差异更聚焦。
