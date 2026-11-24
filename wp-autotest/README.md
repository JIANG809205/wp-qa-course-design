# wp-autotest · WordPress Web 自动化测试工程

> 实测结果：**9 条用例全部通过，耗时约 26 秒**，报告在 `result/surefire-reports/index.html`。

---

## 一、技术栈

| 组件 | 版本 | 说明 |
|---|---|---|
| Java | 17 | OpenJDK |
| Maven | 3.6.3 | 已配阿里云镜像 |
| Selenium | 4.27.0 | chromedriver 由 Selenium Manager 自动匹配 |
| TestNG | 7.10.2 | 测试框架 |
| Allure | 2.29.0 | 依赖已引入（报告用 TestNG HTML 输出） |
| Chrome | 158 | headless=new 运行 |

## 二、目录结构

```
wp-autotest/
├── pom.xml
├── testng.xml                     # 测试套件（按功能分组）
├── run-tests.sh                   # 一键执行并回传报告
├── install-mu-plugin.sh           # 安装测试环境固定项
├── qa-mu-plugin.php               # 环境固定项源码（经典编辑器/关洪水保护）
├── diag.py / diag2.py             # 定位脚本（排查选择器与分析页面结构）
└── src/test/java/edu/qa/wp/
    ├── Config.java                # 被测地址与 5 个角色账号
    ├── DriverFactory.java         # headless Chrome 工厂
    ├── BaseTest.java              # 建/销浏览器，注入监听器
    ├── TestListener.java          # 失败自动截图 + 记录 URL/标题
    ├── pages/                     # Page Object
    │   ├── LoginPage.java
    │   ├── AdminPage.java         # 仪表盘/新建文章/草稿
    │   └── FrontPage.java         # 前台评论
    └── tests/
        ├── LoginTest.java         # TC-AUTH-001/002/004
        ├── PostTest.java          # TC-POST-001/004
        ├── PermissionTest.java    # TC-PERM-001/002
        └── CommentTest.java       # TC-COMM-001/003
```

## 三、执行

```bash
# WSL 内
bash /mnt/e/软件质量保证与测试课程设计/wp-autotest/run-tests.sh
```

脚本会：确认站点可用 → 同步工程到 `/opt/qa/wp-autotest`（避开中文路径导致的 Java 异常）→ `mvn test` → 汇总 → 回传 `result/`。

## 四、用例覆盖（9 条）

| 用例 ID | 用例标题 | 测试方法 | 结果 |
|---|---|---|---|
| TC-AUTH-001 | 管理员正确登录 | `LoginTest#adminLoginSuccess` | ✅ |
| TC-AUTH-002 | 密码错误被拒 | `LoginTest#wrongPasswordRejected` | ✅ |
| TC-AUTH-004 | 用户名为空校验 | `LoginTest#emptyUsernameRejected` | ✅ |
| TC-POST-001 | 新建文章存草稿 | `PostTest#createDraftPost` | ✅ |
| TC-POST-004 | 空标题存草稿 | `PostTest#emptyTitleDraft` | ✅ |
| TC-PERM-001 | 投稿者无发布权限 | `PermissionTest#contributorCannotPublish` | ✅ |
| TC-PERM-002 | 订阅者不能进后台 | `PermissionTest#subscriberCannotEnterAdmin` | ✅ |
| TC-COMM-001 | 匿名评论进待审 | `CommentTest#commentNeedsModeration` | ✅ |
| TC-COMM-003 | 评论脚本被转义 | `CommentTest#commentScriptEscaped` | ✅ |

## 五、测试环境的两个固定项（必须说明）

自动化脚本要对齐“稳定可控”的环境，因此装了一个 mu-plugin（`qa-mu-plugin.php`）：

1. **关闭区块编辑器，统一经典编辑器**。WordPress 7.1.5 默认 Gutenberg，标题不是 `#title` 而是区块内元素，且首次进入有“欢迎使用编辑器”弹窗，脚本极易失效。这是**环境配置选择**，不是绕过测试；报告里应作为“环境固定项”如实写明。
2. **关闭评论洪水保护**。三条评论用例连续提交，会触发 “您提交评论的速度太快了”。生产环境应保留该保护——这一点正好可以作为“安全性建议”写进报告。

## 六、踩过的坑（可直接写进报告“遇到问题及解决”）

| 现象 | 原因 | 解决 |
|---|---|---|
| 新建文章页找不到 `#title` | WP 7.x 默认区块编辑器 | 关闭区块编辑器 + 关闭欢迎弹窗 |
| 投稿者“无发布按钮”断言失败 | WP 7.1.5 中文包文案是“**提交复审**”，不是“提交审核”；且与管理员共用 `#publish` 元素 | 按按钮 `value` 文案断言，而非元素 id |
| 第二条评论用例超时 | WordPress 评论洪水保护（同一文章连续提交） | 测试环境关闭 `check_comment_flood` |
| 评论提交后页面不跳转 | WP 提交后展示“等待审核”预览页，URL 仍在原页 | 断言页面出现“等待审核”，而非等待元素失效 |
| Maven 编译报 `illegal character '\ufeff'` | PowerShell 写文件带 BOM | 改用无 BOM 写入 |
| Java 读中文路径异常 | 与 JMeter 同源的 `sun.jnu.encoding` 问题 | 工程同步到 `/opt/qa` 的 ASCII 路径执行 |

## 七、失败截图

`TestListener` 在用例失败时自动截图，保存到 `target/screenshots/` 并附加到 Allure 报告，同时记录失败时的 URL 与页面标题。本次 9 条全部通过，因此 `result/screenshots/` 里保留的是调试阶段的历史截图，可作为“失败现场取证”能力的示例。
