# WordPress 测试环境（Docker 正式方案 · 已在本机跑通）

> 实测状态：`wp-app` / `wp-db` / `wp-redis` 三容器运行中，站点 <http://localhost:8080> 返回 200，
> 数据 1000 篇文章 / 20000 条评论 / 5 个角色账号，Selenium 已能登录后台并截图（见 `screenshots/`）。

---

## 一、最终架构

```
Windows 11
└── WSL2 (Ubuntu 22.04, 内核 6.18.58.1-microsoft-standard-WSL2, 10GB 内存)
    └── Docker Engine 29.1.3 (dockerd 手动启动 + setsid 保活)
        ├── wp-app    qa/wordpress:7.1.5   Apache 2.4 + PHP 8.1   0.0.0.0:8080
        ├── wp-db     qa/mariadb:10.6      MariaDB, 仅集群内可达
        └── wp-redis  redis:7-alpine       对象缓存
```

镜像来源说明（重要）：

| 镜像 | 来源 | 原因 |
|---|---|---|
| `qa/wordpress:7.1.5` | **本地构建** | 官方镜像拉不动（见第二节） |
| `qa/mariadb:10.6` | **本地构建** | 同上 |
| `ubuntu:jammy-local` | debootstrap + `docker import` | 提供构建底座 |
| `redis:7-alpine` | 官方仓库（约 58MB，拉取成功） | 体积小，能拉下来 |

---

## 二、为什么镜像要本地构建（踩坑记录）

| 尝试 | 结果 |
|---|---|
| 直接用官方镜像 `wordpress:6.6.2` | 走 `hub.rat.dev` 加速，15 分钟只下 70MB，速率约 20–80 KB/s |
| 测试 10 个公共加速站 | 仅 `hub.rat.dev` 可用，且晚高峰极不稳定 |
| 直连 Docker Hub | 超时 |
| **debootstrap + 本地 Dockerfile** | ✅ 走阿里云 apt（约 800 KB/s），两个镜像各 10 分钟内构建完成 |

另外，本机原先的 WSL 内核是实验用 `6.6.123.2-oslab`，**缺 bridge 模块**，dockerd 报
`Failed to create bridge docker0`。已切回微软官方内核：

- 原配置备份：`C:\Users\HP\.wslconfig.oslab-backup`
- 恢复方法：把 `.wslconfig` 里 `#kernel=D:\\oslab\\bzImage-oslab` 的注释去掉，再 `wsl --shutdown`

---

## 三、启动 / 停止

```powershell
cd E:\软件质量保证与测试课程设计\wp-env\local
.\control.ps1 start     # 启动 dockerd + 容器栈（含 WSL 保活进程）
.\control.ps1 status    # 容器状态 + 4 个 URL 状态码 + 数据统计
.\control.ps1 stop      # 停止容器（保留数据）
.\control.ps1 reset     # 删除容器与数据卷（重新初始化用）
```

> WSL 会在空闲时回收虚拟机，导致 dockerd 与容器全部停止。`start` 会拉起 `dsh-wp-keepalive`
> 常驻进程钉住 VM；若发现站点打不开，先执行一次 `.\control.ps1 start`。

---

## 四、账号与数据

| 角色 | 账号 | 密码 |
|---|---|---|
| 管理员 | `admin` | `Admin@2026` |
| 编辑 | `editor` | `Editor@2026` |
| 作者 | `author` | `Author@2026` |
| 投稿者 | `contributor` | `Contributor@2026` |
| 订阅者 | `subscriber` | `Subscriber@2026` |

- 应用密码（接口测试鉴权）：`XEGi7fGumRRl8PJmbE7RDRMx`（author）
- 数据基线：文章 1000 篇、评论 20000 条、固定链接 `/%postname%/`、评论必须人工审核

```bash
curl -u 'author:XEGi7fGumRRl8PJmbE7RDRMx' http://localhost:8080/wp-json/wp/v2/users/me
```

---

## 五、文件说明

| 文件 | 作用 |
|---|---|
| `docker-compose.local.yml` | 正式编排（本地镜像 + 8080 端口） |
| `mariadb/Dockerfile` `mariadb/entrypoint.sh` | MariaDB 镜像：启动后幂等建库建号，绑定 0.0.0.0 |
| `wordpress/Dockerfile` `wordpress/init.sh` | WordPress 镜像：构建期打包 WP 7.1.5，运行期生成 wp-config |
| `stack.sh` `control.ps1` | 启停/状态/重置 |
| `build-images.sh` | 一键构建两个镜像 |
| `screenshot.py` | Selenium 截图脚本 |
| `../native/` | 原生 LAMP 备用方案（Docker 不可用时） |
| `../screenshots/` | 已抓取的后台/前台/文章列表截图 |

---

## 六、工具链（均已安装并验证）

| 类别 | 工具 | 版本 | 状态 |
|---|---|---|---|
| 运行时 | OpenJDK | 17.0.21.1 | ✅ |
| 构建 | Maven | 3.6.3（阿里云镜像已配置） | ✅ |
| 功能自动化 | Selenium（Java/Python） | Java 4.27.0 / Python 4.53.0 | ✅ 依赖已解析 |
| 测试框架 | TestNG | 7.10.2 | ✅ |
| 浏览器 | Google Chrome | 158.0.8127.36 | ✅ headless 可用 |
| 驱动 | chromedriver | 由 Selenium Manager 自动匹配 | ✅ |
| 报告 | Allure（Java 依赖） | 2.29.0 | ✅ |
| 报告 | pytest-html | 已装 | ✅ |
| 性能 | Apache JMeter | 5.6.3 | ✅ 非 GUI 压测通过 |
| 接口 | Newman | 6.2.3 | ✅ |
| 安全 | Nikto / sqlmap | 1.5 / 1.6.4 | ✅ |
| 数据 | Faker / openai SDK | 已装 | ✅ |
| 容器 | Docker Engine + Compose | 29.1.3 / 2.40.3 | ✅ |

> 说明：OWASP ZAP 官方安装包托管在 GitHub Releases，本机网络无法访问，因此安全测试改用
> **Nikto + sqlmap + 手工越权/CSRF 验证**；报告里如实说明工具替代原因即可，不影响评分。

---

## 七、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 站点打不开 / 容器全停 | WSL 空闲回收 VM | `.\control.ps1 start` |
| `docker: command not found` | dockerd 未跑 | 同上（`start` 会先起 dockerd） |
| 500 建立数据库连接出错 | db 未就绪或账号未建 | `docker logs wp-db`；`.\control.ps1 reset` 后重来 |
| REST `/wp-json/` 404 | `.htaccess` 或 AllowOverride 未生效 | 已固化进镜像，若仍 404 执行 `docker exec wp-app apache2ctl graceful` |
| 端口 8080 被占 | 原生 Apache 仍在跑 | `wsl -d Ubuntu-22.04 -u root -- service apache2 stop` |
| 想重新初始化数据 | — | `.\control.ps1 reset` → `.\control.ps1 start` → 重新执行 seed |

---

## 八、重新初始化（完全重建）

```bash
# WSL 内执行
bash /mnt/e/软件质量保证与测试课程设计/wp-env/local/build-images.sh   # 构建镜像
bash /mnt/e/软件质量保证与测试课程设计/wp-env/local/stack.sh start
docker cp /mnt/e/软件质量保证与测试课程设计/wp-env/native/wp-setup.php wp-app:/tmp/
docker exec -e POST_COUNT=1000 -e COMMENT_COUNT=20000 wp-app \
  php /tmp/wp-setup.php http://localhost:8080 WP-QA-Lab admin Admin@2026 admin@example.com
```
