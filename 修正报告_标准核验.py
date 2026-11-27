# -*- coding: utf-8 -*-
"""按标准核验结论修正报告正文。"""

import io
import os
import re

P = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"
t = io.open(P, encoding="utf-8").read()
orig = t


def rep(old, new, count=1):
    global t
    if old not in t:
        print("未找到:", old[:40].replace("\n", " "))
        return
    t = t.replace(old, new, count)


# ---------- 1) 修正 DEF-004 / DEF-005 互换 ----------
rep("| P01 | 安全响应头（4 项） | 全部缺失 | DEF-005 |",
    "| P01 | 安全响应头（4 项） | 全部缺失 | DEF-004 |")
rep("| P05 | XML-RPC 方法列表 | 200，方法可列举 | DEF-004 |",
    "| P05 | XML-RPC 方法列表 | 200，方法可列举 | DEF-005 |")
rep("| DEF-004 | P2 | 安全配置 | XML-RPC 开放，支持 system.listMethods | 200 / methodResponse |\n| DEF-005 | P2 | 安全配置 | 缺少 4 项安全响应头 | 响应头仅 4 项 |",
    "| DEF-004 | P2 | 安全配置 | 缺少 4 项安全响应头 | 响应头仅 4 项 |\n| DEF-005 | P2 | 安全配置 | XML-RPC 开放，支持 system.listMethods | 200 / methodResponse |")

# ---------- 2) 需求清单补 R11 ----------
rep("| R10 | 安全防护 | 信息泄露、XML-RPC、CSRF、上传目录、登录爆破 | TC-SEC-001 | 1 |",
    "| R10 | 安全防护 | 信息泄露、XML-RPC、CSRF、上传目录、登录爆破 | TC-SEC-001 | 1 |\n"
    "| R11 | 兼容性 | 两种浏览器 × 三视口 × 四页面，无横向溢出 | TC-COMP-001~003 | 3 |")
rep("需求从系统功能与质量属性两侧提取，共 10 项，每项都落到具体用例，覆盖率为 100%（追溯矩阵见附录 D）。",
    "需求从系统功能与质量属性两侧提取，共 11 项，每项都落到具体用例，覆盖率为 100%（追溯矩阵见附录 D）。")

# ---------- 3) 追溯矩阵补 R11 ----------
rep("| R10 | 安全防护 | TC-SEC-001 | 1 | 100% |",
    "| R10 | 安全防护 | TC-SEC-001 | 1 | 100% |\n"
    "| R11 | 兼容性 | TC-COMP-001 ~ TC-COMP-003 | 3 | 100% |")
rep("10 项测试需求全部有对应用例，覆盖率为 100%，逐项追溯关系如下表。",
    "11 项测试需求全部有对应用例（合计 43 条），覆盖率为 100%，逐项追溯关系如下表。")
rep("10 项测试需求全部有对应用例，需求—用例追溯矩阵见附录 D。",
    "11 项测试需求全部有对应用例，需求—用例追溯矩阵见附录 D。")

# ---------- 4) debug.log 字节数改为区间 ----------
rep("| P02 | debug.log 可访问性 | 200，9283 字节 | DEF-002 |",
    "| P02 | debug.log 可访问性 | 200，约 9–10 KB（随错误累积增长） | DEF-002 |")
rep("DEF-002：调试日志可匿名下载。未登录访问 `/wp-content/debug.log` 返回 200、9283 字节，",
    "DEF-002：调试日志可匿名下载。未登录访问 `/wp-content/debug.log` 返回 200、约 9–10 KB"
    "（核验时 9920 字节，随错误累积增长），")
rep("| DEF-002 | P1 | 安全配置 | debug.log 可匿名下载，泄露绝对路径 | 200 / 9283 字节 |",
    "| DEF-002 | P1 | 安全配置 | debug.log 可匿名下载，泄露绝对路径 | 200 / 约 9–10 KB |")
rep("安全探针复核 | debug.log 200（9283 字节）",
    "安全探针复核 | debug.log 200（核验时 9920 字节）")

# ---------- 5) 数据基线统一 ----------
rep("| 数据库 | MariaDB | 10.6.23 | 存储 1000 篇文章、20003 条评论 |",
    "| 数据库 | MariaDB | 10.6.23 | 存储 1000 篇文章、20000 条评论（测试残留已清理） |")
rep("| 数据基线 | 1000 篇文章、20003 条评论、6 个角色账号 |",
    "| 数据基线 | 1000 篇文章、20000 条评论、6 个角色账号（测试残留已清理，核验时已复原） |")

# ---------- 6) 复跑耗时标注日期 ----------
rep("执行时 9 条 UI 用例全部通过（首次 25.96 秒，2026-11-26 复跑 35.1 秒）",
    "执行时 9 条 UI 用例全部通过（首轮 25.96 秒；2026-11-26 复跑 35.1 秒；"
    "2026-11-27 证据归档复跑 40.55 秒，Maven 全流程 51.88 秒）")
rep("| 接口回归（pytest 26 条） | 26 通过 / 0 失败，86.35 秒 | 与归档一致 |",
    "| 接口回归（pytest 26 条） | 26 通过 / 0 失败；11-26 复跑 86.35 秒、11-27 归档 59.38 秒（均为不同轮次，非同一轮差异） | 与归档一致 |")
rep("| UI 端到端（TestNG 9 条） | 9 通过 / 0 失败，35.1 秒 |",
    "| UI 端到端（TestNG 9 条） | 9 通过 / 0 失败；11-26 复跑 35.1 秒、11-27 归档 40.55 秒 |")

# ---------- 7) 局限补 4 项 ----------
rep("局限也需说明：性能压测与被测系统同机，TPS 绝对值偏低；兼容性未覆盖 Safari；权限矩阵未覆盖插件扩展角色；"
    "DeepSeek-V4-Pro 因推理耗时较长，用例任务只跑了 1 轮，未给出置信区间。这些均已在相应章节标注。",
    "局限也需说明。测试类型上，未做人工代码审查与静态分析（被测对象为第三方开源代码），"
    "未做恢复测试与长时间稳定性测试；安全侧未覆盖 TLS/加密传输，且未做渗透式攻击链验证；"
    "可访问性（WCAG）完全未测。环境与方法上，性能压测与被测系统同机，TPS 绝对值偏低；"
    "兼容性未覆盖 Safari 与移动真机；权限矩阵未覆盖插件扩展角色；"
    "DeepSeek-V4-Pro 因推理耗时较长，用例任务只跑了 1 轮，未给出置信区间。"
    "以上均在相应章节或附录 E 的标准对照中标注。")

# ---------- 8) 新增附录 E / F / G ----------
appendix = """

## 附录 E　标准符合性对照

按 GB/T 15532-2008、GB/T 9386-2008、ISO/IEC/IEEE 29119-2/3、ISO/IEC 25010、OWASP WSTG 逐项对照，结论如下（完整版见《标准符合性核验报告》）。

表E.1 测试类型覆盖（GB/T 15532-2008）

| 测试类型 | 覆盖 | 本次对应 |
|---|---|---|
| 功能测试 | 完整 | 43 条用例，双栈自动化 |
| 性能测试 | 完整 | 2 场景 × 3 级 × 3 次 × 60 秒 + CPU |
| 接口测试 | 完整 | 26 条 REST 用例 + 36 格权限矩阵 |
| 安全性测试 | 完整 | 23 项探针 + 双版本对照 + 加固复测 |
| 兼容性测试 | 完整 | 24 组（2 浏览器 × 3 视口 × 4 页面） |
| 边界测试 | 完整 | 上传大小、分页、标题长度 |
| 强度测试 | 完整 | 100 并发（列表页劣化） |
| 人机界面测试 | 部分 | 仅视口适配，未做可用性 |
| 文档审查 | 部分 | 有交叉评审，无正式评审记录 |
| 静态分析 | 部分 | 加固文件 `php -l`；未分析核心 |
| 安装测试 | 部分 | 一键重建；无多环境矩阵 |
| 可靠性测试 | 部分 | 60 秒稳态；无长稳 |
| 余量测试 | 部分 | 容量观察；无定量测算 |
| 代码审查 | 未覆盖 | 第三方开源代码，未走查 |
| 恢复测试 | 未覆盖 | 无故障注入 |

表E.2 质量特性覆盖（ISO/IEC 25010）

| 特性 | 覆盖 | 证据 |
|---|---|---|
| 功能适合性 | 完整 | 43 条用例，90.7% 通过 |
| 性能效率 | 完整 | TPS / P95 / CPU + 瓶颈定位 |
| 兼容性 | 完整 | 24 组跨浏览器视口 |
| 安全性 | 完整 | 探针 11/12 → 2/12 |
| 易用性 | 部分 | 仅视口；无可用性测试 |
| 可靠性 | 部分 | 稳态 0 错误；无长稳 |
| 可维护性 | 部分 | 结构说明与 CI；无静态度量 |
| 可移植性 | 部分 | Docker 重建；无跨平台矩阵 |

表E.3 Web 安全类别覆盖（OWASP WSTG）

| 类别 | 覆盖 | 说明 |
|---|---|---|
| 信息收集 / 配置 / 身份 / 认证 / 授权 / 错误处理 / API | 完整 | 见 5.5 节探针表 |
| 会话管理 / 输入验证 / 业务逻辑 / 客户端 | 部分 | 测了 nonce、XSS 载荷、状态迁移、响应式 |
| 加密传输 | 未覆盖 | 本地 HTTP 环境，未测 TLS |

表E.4 测试文档齐备性（GB/T 9386-2008 / 29119-3）

| 文档 | 对应产物 | 状态 |
|---|---|---|
| 测试计划 | 报告第 2 章 | 齐备 |
| 测试设计说明 | 2.7 节 + 用例表设计方法列 | 齐备 |
| 测试用例说明 | 用例工作簿（43 条） | 齐备 |
| 测试规程 | `run.sh`、`verify-*.sh` | 齐备 |
| 测试记录 | `evidence/` 日志与截图 | 齐备 |
| 测试结果与完成报告 | 第 5 章、第 9 章、附录 C | 齐备 |
| 缺陷报告 | 缺陷清单 + 工作簿缺陷表 | 齐备 |

## 附录 F　术语与缩写

| 术语 | 含义 |
|---|---|
| CMS | 内容管理系统（Content Management System） |
| SUT | 被测系统（System Under Test） |
| POM | 页面对象模型（Page Object Model） |
| TPS | 每秒事务数（Transactions Per Second） |
| P95 | 95 分位响应时间 |
| CI | 持续集成（Continuous Integration） |
| DOM | 文档对象模型 |
| Wilson 区间 | 小样本下比例指标的置信区间估计方法 |
| mu-plugin | WordPress 的强制启用插件（must-use plugin） |
| nonce | WordPress 的一次性安全令牌，用于防 CSRF |

## 附录 G　参考文献

1. GB/T 15532-2008 计算机软件测试规范. 北京: 中国标准出版社, 2008.
2. GB/T 9386-2008 计算机软件测试文档编制规范. 北京: 中国标准出版社, 2008.
3. ISO/IEC/IEEE 29119-2:2021 Software and systems engineering — Software testing — Part 2: Test processes.
4. ISO/IEC/IEEE 29119-3:2021 Software and systems engineering — Software testing — Part 3: Test documentation.
5. ISO/IEC 25010:2011 Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models.
6. OWASP. Web Security Testing Guide (WSTG), latest edition. https://owasp.org/www-project-web-security-testing-guide/
7. ISTQB. Certified Tester Foundation Level Syllabus.
8. W3C. Web Content Accessibility Guidelines (WCAG) 2.1.
9. Vali D K. Autonomous QA Agent: A Retrieval-Augmented Framework for Reliable Selenium Script Generation. arXiv:2601.06034, 2025.
10. Júnior E, Valejo A, Valverde-Rebaza J, et al. GenIA-E2ETest: A Generative AI-Based Approach for End-to-End Test Automation. SBES 2025. arXiv:2510.01024.
11. Kim H, Kim S. MacroBench: A Novel Testbed for Web Automation Scripts via Large Language Models. NeurIPS 2025 Workshop. arXiv:2510.04363.
"""
if "## 附录 E　标准符合性对照" not in t:
    t = t.rstrip() + appendix

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("修改完成；文件长度:", len(t), "原:", len(orig))
print("DEF-004 出现次数:", t.count("DEF-004"), "DEF-005:", t.count("DEF-005"))
print("R11 出现次数:", t.count("R11"))
