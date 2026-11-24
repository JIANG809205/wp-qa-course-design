> ⚠️ **数据说明（2026-11-24 更新）**
> 下表是**初步梯度探索**：每线程 10 次循环、单轮 5–22 秒，统计时长把爬坡期算进了分母，且未重复。
> 严谨复测（60 秒稳态 × 3 次取中位数 + CPU 采样）见 [`性能复测结果.md`](性能复测结果.md)，
> 新数据：静态首页 122.8/126.7/127.5 TPS，列表页 229.0/229.9/186.4 TPS，容器 CPU 590%–650%。
> **两组数据不可直接比较**，报告以复测数据为准，下表仅作过程记录。
# wp-perf · WordPress 性能测试与优化实验

> 实测环境：Docker 三容器（WordPress 7.1.5 / MariaDB 10.6 / Redis 7），宿主机 8 vCPU。
> 测试工具：Apache JMeter 5.6.3（非 GUI 模式），每场景固定循环 10 次，ramp-up 5 秒。

---

## 一、测试设计

| 场景 | 路径 | 说明 |
|---|---|---|
| 首页 | `/` | 渲染 10 篇文章列表，查询最重 |
| 文章详情 | `/?p=<id>` | 单篇渲染 + 评论查询 |
| 搜索结果 | `/?s=test` | 涉及全表 LIKE 查询 |
| 后台文章列表 | `/wp-admin/edit.php` | 含登录（Cookie + 302） |

并发梯度：10 / 50 / 100 / 200 线程。共 11 组有效运行，**全部 0 错误**。

## 二、基线结果

| 场景 | 并发 | 样本 | TPS | 平均响应(ms) | P95(ms) |
|---|---|---|---|---|---|
| 首页 | 10 | 100 | 19.6 | 81 | 121 |
| 首页 | 50 | 500 | 84.1 | 143 | 263 |
| 首页 | 100 | 1000 | **91.5** | 519 | 1549 |
| 首页 | 200 | 2000 | **90.3** | 1457 | 5272 |
| 文章详情 | 10 | 300 | 56.4 | 69 | 121 |
| 文章详情 | 50 | 1500 | 208.5 | 163 | 379 |
| 文章详情 | 100 | 3000 | **221.5** | 596 | 1365 |
| 搜索结果 | 10 | 100 | 19.7 | 75 | 104 |
| 搜索结果 | 50 | 500 | 91.8 | 75 | 94 |
| 搜索结果 | 100 | 1000 | **104.2** | 500 | 929 |
| 后台列表 | 10 | 50 | 9.6 | 96 | 121 |
| 后台列表 | 50 | 250 | **42.1** | 113 | 225 |

图表：`charts/tps.png`、`charts/response-time.png`、`charts/admin.png`；
原始数据：`summary.csv`；JMeter 仪表盘：`report-home-200/`、`report-admin-50/`。

## 三、瓶颈定位（三步推论）

1. **首页在 90 TPS 处饱和**：并发从 100 增到 200，TPS 只从 91.5 变到 90.3，但平均响应时间从 519ms 涨到 1457ms，P95 从 1549ms 涨到 5272ms —— 典型的**排队**特征，说明系统已到处理上限。
2. **单请求 CPU 约 80ms**：10 并发时平均 81ms，8 vCPU 理论上限 ≈ 8 / 0.08 = **100 TPS**，实测 90+ 已贴近理论上限。文章详情页更轻（221 TPS）反向印证了“单请求耗时决定吞吐”。
3. **排除并发配置**：Apache prefork `MaxRequestWorkers` 默认 150，是 200 线程时的可疑点。把它提到 300、并把 MariaDB `innodb_buffer_pool_size` 提到 512M 后复压，**TPS 91.5 → 91.6（+0.1%）**，P95 反而略升 —— 说明瓶颈不在 worker 数或数据库缓冲池。

## 四、两次优化实验（含一次负结果）

| 实验 | 改动 | 100 并发 TPS | 结论 |
|---|---|---|---|
| 基线 | — | 91.5 | — |
| 参数调优 | Apache workers 150→300；InnoDB buffer pool 128M→512M；OPcache 调整 | 91.6 | **无效**，瓶颈不在此 |
| 页面缓存 | 启用 `mod_cache` + `mod_cache_disk`，缓存前台 GET 60 秒 | 89.0 | **未生效**，详见下 |

`charts/optimization-compare.png` 是三者对比。

### 页面缓存为什么没生效（重要发现）

```bash
curl -sI http://localhost:8080/ | grep -iE "vary|cache-control|expires"
# 无任何缓存相关响应头
du -sh /var/cache/apache2/mod_cache_disk   # 4.0K，缓存目录为空
```

两个原因叠加：
1. WordPress 前台**默认不发送 `Cache-Control` / `Expires`**，Apache 拿不到缓存指令；
2. WordPress 对匿名请求仍会发送 `Vary: Cookie`，而 `mod_cache` 会**拒绝缓存带 Vary 的响应**，因此即使配置了 `CacheDefaultExpire` 也不会落盘。

结论：**在 WordPress 上做页面缓存，必须由应用层（插件/静态化）完成，不能指望 Apache 的 `mod_cache` 直接接管。**

## 五、结论与改进建议

| 结论 | 依据 |
|---|---|
| 单机 PHP 渲染能力：首页 ~90 TPS，详情页 ~220 TPS | 11 组梯度压测 |
| 瓶颈是 CPU（单请求 ~80ms），不是并发上限或数据库缓冲 | worker 150→300 无改善 |
| Apache `mod_cache` 不适用于 WordPress | 无缓存头 + `Vary: Cookie`，缓存目录为空 |
| 后台管理页明显更慢（42 TPS） | 含登录流程 + 后台多查询 |

**有效的优化方向**（按性价比排序）：
1. **对象缓存**：Redis 对象缓存可显著减少重复查询（本机因网络原因装不上 `php-redis` 扩展与插件，未做实测）；
2. **页面静态化**：把首页/详情页生成静态 HTML（如 WP Super Cache 的“静态文件”模式），可绕过 PHP 渲染；
3. **增加 vCPU**：当前 8 核，理论上线性提升到 ~180 TPS；
4. **CDN/反向代理**：Nginx + FastCGI Cache 比 Apache `mod_cache` 更适合 WordPress。

## 六、关于 GPU（结论：与本测试无关）

本机有 RTX 4060 Laptop 8GB，但**对 WordPress 性能测试没有帮助**：

- WordPress 是 PHP 脚本解释 + MySQL 查询，全部跑在 CPU 上，PHP/Apache 没有任何 GPU 计算路径；
- 瓶颈是单请求 80ms 的 CPU 时间，GPU 无法并行化“一次 HTTP 请求内的串行逻辑”；
- GPU 唯一有用的场景是**本地大模型推理**（例如用 Ollama 跑 DeepSeek-R1-Distill-7B，8GB 显存可跑 4-bit 量化版），属于“大模型应用”章节的素材，不是性能测试项。

## 七、文件与复现

```
wp-perf/
├── jmx/perf.jmx            # 参数化压测计划（-Jpath/-Jthreads/-Jramp/-Jloops）
├── jmx/perf-admin.jmx      # 后台场景（含登录）
├── run-perf.sh             # 跑完整矩阵（4 场景 × 并发梯度）
├── analyze.py              # 解析 jtl → summary.csv + 三张图
├── make-html-report.sh     # 生成 JMeter HTML 仪表盘
├── hot-cache.sh            # 运行时启用 mod_cache 并复压
├── results/                # 基线 jtl
├── results-tuned/          # 参数调优后 jtl
├── results-cache/          # 页面缓存后 jtl
├── summary.csv
├── charts/
└── report-home-200/  report-admin-50/  report-home-100/
```

复现：

```bash
bash /mnt/e/软件质量保证与测试课程设计/wp-perf/run-perf.sh
/opt/qa-venv/bin/python /mnt/e/软件质量保证与测试课程设计/wp-perf/analyze.py
```

## 八、注意事项

- **JMeter 必须在 ASCII 路径下运行**（`cd /opt`），否则 Java 读取中文路径会抛 `InvalidPathException`；
- **docker 守护进程会被 WSL 回收**：长时间无 WSL 进程时虚拟机shutdown，容器随之停止。执行压测前先确认 `docker info` 可用，否则先 `nohup setsid dockerd &`；
- 压测期间不要同时跑 Selenium 或 IDE，否则宿主机 CPU 争用会让数据失真（本次测试均在空闲状态执行）。
