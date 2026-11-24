# -*- coding: utf-8 -*-
"""扩充报告内容：增加用例明细、缺陷全表、探针表、提示词示例与附录。"""

import io

P = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
t = io.open(P, encoding="utf-8").read()

# ---------- 1) 功能测试：补用例设计方法表、代码片段、后台截图 ----------
anchor = "四条失败用例分别对应 DEF-001"
add1 = """用例设计方法的分布如下表，可以看出等价类与边界值主要用于输入类场景，状态迁移与场景法主要用于流程类场景。

表6.2 用例设计方法分布

| 设计方法 | 用例数 | 典型场景 | 代表性用例 |
|---|---|---|---|
| 等价类划分 | 12 | 登录、表单字段、参数校验 | TC-AUTH-002 错误密码登录 |
| 边界值分析 | 9 | 分页、文件大小、标题长度 | TC-MEDIA-002 超限文件上传 |
| 状态迁移 | 6 | 文章状态、评论状态 | TC-POST-002 草稿→待审→发布 |
| 场景法 | 7 | 端到端业务流程 | TC-PERM-001 投稿者提交流程 |
| 错误推测 | 5 | 安全与上传 | TC-MEDIA-003 伪装可执行文件 |
| 权限矩阵 | 4 | 角色隔离 | TC-PERM-004 编辑越权建用户 |

自动化脚本按 Page Object 组织，页面元素与操作分离。以登录用例为例，核心代码如下：

```java
public class LoginPage {
    private final WebDriver driver;
    @FindBy(id = "user_login") private WebElement userLogin;
    @FindBy(id = "user_pass")  private WebElement userPass;
    @FindBy(id = "wp-submit")  private WebElement submit;

    public LoginPage(WebDriver driver) { this.driver = driver; }

    public AdminPage loginAs(String user, String pass) {
        userLogin.clear(); userLogin.sendKeys(user);
        userPass.clear();  userPass.sendKeys(pass);
        submit.click();
        return new AdminPage(driver);
    }
}
```

执行时 9 条 UI 用例全部通过，总耗时 25.96 秒，失败自动截图并写入 Allure 报告。后台文章列表的实际界面如下图所示。

[[图:posts|图6.3 后台文章列表界面（1000 篇文章基线）]]

四条失败用例分别对应 DEF-001"""
if anchor in t and "[[图:posts" not in t:
    t = t.replace(anchor, add1, 1)

# ---------- 2) 缺陷分析：补完整缺陷表 ----------
anchor2 = "缺陷分布上有一个明显特征"
add2 = """11 条缺陷的完整清单如下表。

表6.8 缺陷清单（11 条 + 1 观察项）

| 编号 | 等级 | 模块 | 问题描述 | 关键证据 |
|---|---|---|---|---|
| DEF-001 | P1 | 登录 | 登录无失败次数限制，可无限尝试 | 连续 6 次错误密码均返回 200 |
| DEF-002 | P1 | 安全配置 | debug.log 可匿名下载，泄露绝对路径 | 200 / 4437 字节 |
| DEF-003 | P2 | 安全配置 | 上传目录可浏览（Index of） | 200 / 目录列表 |
| DEF-004 | P2 | 安全配置 | XML-RPC 开放，支持 system.listMethods | 200 / methodResponse |
| DEF-005 | P2 | 安全配置 | 缺少 4 项安全响应头 | 响应头仅 4 项 |
| DEF-006 | P2 | REST API | 用户列表匿名可读，泄露作者 slug | 200 / 用户数组 |
| DEF-012 | P2 | 安全配置 | `?author=N` 可枚举用户名 | 301 跳转 /author/admin/ |
| DEF-008 | P3 | 媒体库 | 0 字节文件上传返回 500 | 500 / rest_upload_unknown_error |
| DEF-009 | P3 | 媒体库 | 超限文件错误码语义不准 | 400 / no_content_disposition |
| DEF-010 | P3 | 安全配置 | Server 头暴露 Apache 版本 | Apache/2.4.52 (Ubuntu) |
| DEF-011 | P3 | 用户与角色 | 重复用户名返回 500 而非 400 | 500 / existing_user_login |
| DEF-007 | 观察 | 评论 | 洪水保护对正常用户误伤 | 15 秒内二次提交被拦 |

其中 DEF-002 的复现证据如下图所示，可以看到日志完整暴露了服务器绝对路径。

[[图:debug-log|图6.7 DEF-002 证据：debug.log 泄露绝对路径]]

缺陷分布上有一个明显特征"""
if anchor2 in t and "[[图:debug-log" not in t:
    t = t.replace(anchor2, add2, 1)

# ---------- 3) 安全测试：补探针结果表 ----------
anchor3 = "为判断问题是否为版本回归"
add3 = """23 项探针的执行结果汇总如下表（仅列出有代表性的 12 项）。

表6.9 安全探针执行结果（节选）

| 探针 | 检查内容 | 结果 | 对应缺陷 |
|---|---|---|---|
| P01 | 安全响应头（4 项） | 全部缺失 | DEF-005 |
| P02 | debug.log 可访问性 | 200，4437 字节 | DEF-002 |
| P03 | 上传目录索引 | 200，目录可列出 | DEF-003 |
| P04 | readme.html | 200，不含版本号 | 观察 |
| P05 | XML-RPC 方法列表 | 200，方法可列举 | DEF-004 |
| P06 | `?author=1` 枚举 | 301 跳转 | DEF-012 |
| P07 | REST 用户匿名读取 | 200，返回用户数组 | DEF-006 |
| P08 | 0 字节文件上传 | 500 | DEF-008 |
| P09 | 重复用户名创建 | 500 | DEF-011 |
| P10 | 登录失败限制 | 无锁定、无验证码 | DEF-001 |
| P11 | 非法参数是否 500 | 400，结构化错误 | 无（正常） |
| P12 | license.txt | 200 | 观察 |

为判断问题是否为版本回归"""
if anchor3 in t and "表6.9" not in t:
    t = t.replace(anchor3, add3, 1)

# ---------- 4) 大模型章节：补提示词示例 ----------
anchor4 = "第一版指标是\"格式合规率 100%\""
add4 = """用例生成使用的提示词骨架如下，三段式结构（角色、输入、输出约束）：

```
你是一位资深软件测试工程师。请针对下面的功能点设计 8 到 10 条测试用例，
覆盖正常、异常与边界场景。

功能点：{{feature}}
可用 UI 元素：{{ui}}
涉及角色：{{roles}}

输出要求：
1) 仅输出 JSON 数组，不要任何解释文字；
2) 每条用例包含字段 id / title / precondition / steps / expected / method；
3) steps 为字符串数组，至少 2 步；
4) method 取值限定为：等价类划分、边界值分析、状态迁移、场景法、错误推测。
```

第一版指标是"格式合规率 100%"""
if anchor4 in t and "你是一位资深软件测试工程师" not in t:
    t = t.replace(anchor4, add4, 1)

# ---------- 5) 附录 ----------
t = t.rstrip() + """

# 附录

## 附录 A　代码与数据仓库结构

| 目录 | 内容 |
|---|---|
| `wp-env/` | Dockerfile、compose 编排、环境脚本 |
| `wp-autotest/` | Selenium + TestNG 工程（9 条 UI 用例） |
| `wp-api-tests/` | pytest 接口用例（26 条） |
| `wp-compat/` | 兼容性测试脚本与 24 组结果 |
| `wp-perf/` | JMeter 计划、压测脚本、原始 jtl、图表 |
| `defect-hunt/` | 安全探针、权限矩阵、缺陷证据 |
| `llm-qa/` | 大模型评测代码、数据集、结果 |
| `.github/workflows/` | 持续集成流水线 |

## 附录 B　复现命令

```bash
# 1. 启动被测环境
bash wp-env/local/stack.sh start

# 2. 功能与接口测试
cd wp-autotest && mvn test
bash wp-api-tests/run.sh

# 3. 性能测试（两场景各 3 级 × 3 次 × 60 秒）
bash wp-perf/rigor-perf.sh
bash wp-perf/rigor-perf-list.sh

# 4. 安全与权限
bash defect-hunt/collect-evidence.sh
bash defect-hunt/matrix-stability.sh

# 5. 大模型评测
cd llm-qa && python scripts96_eval.py --model deepseek-v4.1-flash --outdir /tmp/s96
python selector_fidelity_dom.py
```

## 附录 C　数据核验说明

报告中的 41 项关键数字均由 `核验全部数字.py` 从原始文件重算比对，结果为 41/41 一致。样本量对精度的影响另由 `样本量评估.py` 以 Wilson 区间给出，相关结论已在正文标注置信区间。
"""

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("扩充完成；图标记数:", t.count("[[图:"), "；表标题数:", t.count("\n表"))
