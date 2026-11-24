# 软件质量保证与测试课程设计

**基于 DeepSeek 的开源 CMS 系统 Web 测试与质量评估——以 WordPress 为例**

被测系统：WordPress **7.1.5**（wordpress.org 官方发布包，本地 Docker 部署）
测试范围：功能、接口、性能、安全、兼容性 + 大模型辅助测试评测

---

## 一、快速了解结果

| 项 | 结果 |
|---|---|
| 功能用例 | **43 条全部执行**，通过 39 / 失败 4（通过率 90.7%） |
| 缺陷 | **11 条**（P1×2、P2×5、P3×4）+ 1 观察项，有效率 11/11 |
| 权限矩阵 | **36 格**（6 角色 × 6 操作）× 3 次重复，0 变化、0 越权 |
| 性能 | 静态首页 122.8 / 126.7 / 127.5 TPS；文章列表页 97.3 / 87.8 / 52.1 TPS（60 秒稳态 × 3 次） |
| 安全 | 23 项探针；7.1.4 与 7.1.5 双版本对照各 **11/12**，证明非版本回归 |
| 兼容性 | Chrome + Firefox × 3 视口 × 4 页面 = **24/24 通过** |
| 大模型 | 20 功能点 × 3 轮生成、96 条脚本、24 条归因，全部附 95% 置信区间 |

---

## 二、仓库结构

```
.
├── 00-开题确认书.md            选题论证与风险
├── 01-任务书-填写稿.md
├── 02-选题终审.md
├── 03-测试计划.md              目标、策略、环境、进度、指标
├── 04-权限矩阵.md              预期权限模型
├── 05-测试用例-核心40条.xlsx    43 条用例 + 权限实测 + 缺陷表 + 执行汇总
├── 06-报告章节-大模型使用过程及经验.md
├── 07-参考项目调研.md
├── 报告正文-第1-3章.md
├── 报告正文-第4-5章.md
├── 报告正文-第7-9章.md
├── 项目审查报告.md             自查发现的问题与修复记录
├── 数据核验与样本量评估.md      41 项数字核验 + Wilson 置信区间
│
├── wp-env/                    被测环境（Dockerfile、compose、初始化脚本）
│   ├── local/                 docker-compose.local.yml、wordpress/、mariadb/
│   └── native/                运维脚本（启动、清场、关闭自动更新等）
├── wp-autotest/               Selenium + TestNG 工程（9 条 UI 用例）
├── wp-api-tests/              pytest 接口用例（26 条）
├── wp-compat/                 兼容性（视口矩阵 + Chrome/Firefox）
├── wp-perf/                   性能（JMeter jmx、脚本、图表）
│   └── charts-final/          最终图表
├── defect-hunt/               安全探针、权限矩阵、缺陷清单、证据
│   └── evidence/              缺陷复现截图与响应头
├── llm-qa/                    大模型评测（代码、数据集、结果）
│   ├── data/                  功能点、覆盖点、归因样本、真实 DOM 基准
│   └── outputs/               各模型结果与指标
└── .github/workflows/ci.yml   持续集成（静态检查 / 端到端冒烟 / 评测自检）
```

---

## 三、如何复现

### 1. 启动被测环境

```bash
# 需要 WSL2 + Docker
bash wp-env/local/stack.sh start        # 或使用 control.ps1 start
# 站点：http://localhost:8080（admin / Admin@2026）
```

### 2. 功能测试

```bash
cd wp-autotest && mvn test              # Selenium + TestNG，9 条
bash wp-api-tests/run.sh                # pytest，26 条
```

### 3. 性能测试

```bash
bash wp-perf/rigor-perf.sh              # 静态首页 3 级 × 3 次 × 60 秒
bash wp-perf/rigor-perf-list.sh         # 文章列表页
/opt/qa-venv/bin/python wp-perf/make-charts-final.py   # 生成图表
```

### 4. 安全与权限

```bash
bash defect-hunt/collect-evidence.sh    # 23 项探针 + 证据截图
bash defect-hunt/matrix-stability.sh    # 36 格权限矩阵 × 3 次
```

### 5. 大模型评测

```bash
cd llm-qa
cp .env.example .env                    # 填入 DASHSCOPE_API_KEY
python scripts96_eval.py --model deepseek-v4.1-flash --outdir /tmp/s96
python selector_fidelity_dom.py         # 定位器保真度（真实 DOM 基准）
```

---

## 四、几个值得说明的方法点

1. **权限矩阵用双通道验证**：既看页面元素是否存在，也带 nonce 直调接口。第一版因 nonce 取错导致"4 处越权"的假缺陷，修正后为 0。
2. **定位器保真度以真实 DOM 为基准**：从 9 个后台页面抓取 1181 个 id、193 个 name、769 个 class，而不是手写白名单。修正后三模型保真度从虚高的 30%–57% 回落到 **21%–25%**。
3. **性能数据经过一次作废重测**：初版列表页 URL 触发 301 重定向，测到的是空响应；改用 `/qa-blog/` 重测后结论反转。
4. **样本量用置信区间衡量**：比例指标一律给 Wilson 95% CI，并注明"方向可靠、精确排名不可靠"。

---

## 五、环境固定项

| 项 | 设置 | 原因 |
|---|---|---|
| 自动更新 | `AUTOMATIC_UPDATER_DISABLED` | 防止测试期间核心被静默升级 |
| 固定链接 | `/%postname%/` | 避免 301 影响接口与性能测试 |
| 调试日志 | 开启 `WP_DEBUG_LOG` | 复现"日志可下载"缺陷 |
| 区块编辑器 | 关闭（mu-plugin） | 经典编辑器才有 `#title`，便于定位 |
| 评论洪水保护 | 关闭 | 用例需连续提交评论 |

---

## 六、说明

- `.env`（含 API Key）**未入库**，仓库内提供 `.env.example` 模板。
- 压测原始记录（`.jtl`）、虚拟环境、二进制驱动、已作废的旧报告均未入库，可用对应脚本重新生成。
- 报告中所有数字均可通过 `核验全部数字.py` 回溯到原始数据。
