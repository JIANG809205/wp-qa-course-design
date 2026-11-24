# -*- coding: utf-8 -*-
"""生成《核心 40 条测试用例》工作簿。"""

import os
from collections import Counter

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05-测试用例-核心40条.xlsx")

HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
BODY_FONT = Font(name="微软雅黑", size=10)
TITLE_FONT = Font(name="微软雅黑", size=14, bold=True)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(vertical="center", wrap_text=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

# 用例ID, 模块, 优先级, 标题, 设计方法, 前置条件, 步骤, 预期结果, 需求ID
CASES = [
    ("TC-AUTH-001", "登录与账号", "P0", "管理员使用正确账号密码登录成功",
     "等价类划分", "系统已部署，管理员账号已创建",
     "1. 访问 /wp-login.php\n2. 输入正确用户名与密码\n3. 点击“登录”",
     "跳转至 /wp-admin/ 仪表盘，右上角显示用户名，无任何报错", "R01"),
    ("TC-AUTH-002", "登录与账号", "P0", "密码错误时登录失败并给出提示",
     "等价类划分", "存在有效账号",
     "1. 访问 /wp-login.php\n2. 输入正确用户名 + 错误密码\n3. 点击“登录”",
     "停留在登录页，提示“密码不正确”，不进入后台", "R01"),
    ("TC-AUTH-003", "登录与账号", "P1", "不存在的用户名登录失败且不泄露账号是否存在",
     "等价类划分/安全", "无",
     "1. 输入未注册的用户名 + 任意密码\n2. 提交",
     "登录失败；提示文案与“密码错误”场景不产生明显差异（避免用户名枚举）", "R01"),
    ("TC-AUTH-004", "登录与账号", "P2", "用户名或密码为空时提交的校验",
     "边界值分析", "无",
     "1. 用户名留空，密码填任意值\n2. 提交\n3. 用户名填值，密码留空，提交",
     "两次均被拦截并提示必填，不产生 PHP 报错或白屏", "R01"),
    ("TC-AUTH-005", "登录与账号", "P1", "连续多次错误密码后的系统行为",
     "错误推测", "无锁定类插件",
     "1. 对同一账号连续输入 5 次错误密码\n2. 观察第 6 次及以后的响应",
     "记录实际行为：若仍可无限次尝试，则判定为安全风险并登记缺陷（建议加限流/验证码）", "R01"),

    ("TC-POST-001", "内容管理", "P0", "新建文章并保存为草稿",
     "场景法", "已登录管理员",
     "1. 文章→新建\n2. 填写标题与正文\n3. 点击“保存草稿”",
     "提示已保存草稿；文章状态为“草稿”；前台不可见", "R02"),
    ("TC-POST-002", "内容管理", "P0", "文章状态迁移：草稿→待审→已发布",
     "状态迁移", "存在投稿者账号",
     "1. 投稿者创建文章并提交审核\n2. 编辑登录后台审核通过并发布\n3. 前台查看",
     "状态依次为 草稿→待审核→已发布；前台可正常访问，无 404", "R02"),
    ("TC-POST-003", "内容管理", "P1", "定时发布：设置未来时间后到点自动发布",
     "状态迁移", "站点时区正确，WP-Cron 可用",
     "1. 新建文章\n2. 发布时间设为当前时间 +3 分钟\n3. 等待并刷新",
     "发布前状态为“已安排”；到点后自动变为“已发布”且前台可访问", "R02"),
    ("TC-POST-004", "内容管理", "P1", "标题为空时保存草稿的处理",
     "边界值分析", "已登录",
     "1. 标题留空\n2. 填写正文\n3. 保存草稿",
     "自动生成“自动草稿”类标题或提示保存为草稿，不产生 500 错误", "R02"),
    ("TC-POST-005", "内容管理", "P2", "超长标题（201 字符）的保存与展示",
     "边界值分析", "已登录",
     "1. 标题输入 201 个字符\n2. 发布\n3. 前台查看标题",
     "文章可发布；后台与前台标题完整或按规则截断，不出现乱码/溢出破坏布局", "R02"),
    ("TC-POST-006", "内容管理", "P1", "文章移入回收站、还原、永久删除",
     "状态迁移", "存在已发布文章",
     "1. 移入回收站→查看前台\n2. 回收站中还原→查看前台\n3. 永久删除",
     "移入后前台 404；还原后恢复；永久删除后数据库中不再存在", "R02"),

    ("TC-MEDIA-001", "媒体库", "P0", "上传 JPG 图片并生成多尺寸缩略图",
     "场景法", "已登录，上传上限 2M",
     "1. 媒体→添加新媒体\n2. 上传 500KB JPG\n3. 查看媒体库与附件详情",
     "上传成功；生成多种尺寸；可插入文章并正常显示", "R03"),
    ("TC-MEDIA-002", "媒体库", "P1", "上传超过 PHP 限制的文件",
     "边界值分析", "上传上限 2M",
     "1. 上传 3MB 图片\n2. 观察提示",
     "给出明确的大小超限提示（而非白屏或 500）；界面停留在上传页", "R03"),
    ("TC-MEDIA-003", "媒体库", "P0", "上传伪装成图片的可执行文件被拒绝",
     "错误推测/安全", "已登录",
     "1. 将 shell.php 重命名为 shell.php.jpg\n2. 尝试上传\n3. 检查上传目录",
     "被拒绝或上传后不可执行；上传目录中不存在可执行 PHP 文件", "R03"),
    ("TC-MEDIA-004", "媒体库", "P2", "中文文件名上传后的显示与访问",
     "等价类划分", "已登录",
     "1. 上传名为“测试图片.png”的文件\n2. 在媒体库查看\n3. 复制文件 URL 访问",
     "文件名正常显示（或按规则转写）；URL 可访问，不出现 404/乱码", "R03"),
    ("TC-MEDIA-005", "媒体库", "P2", "上传 0 字节文件",
     "边界值分析", "已登录",
     "1. 上传 0 字节的 png 文件\n2. 观察提示",
     "给出类型或文件损坏提示，不产生 PHP 警告", "R03"),

    ("TC-COMM-001", "评论", "P0", "未登录用户提交评论后进入待审核",
     "场景法", "后台开启“评论须经人工审核”",
     "1. 前台打开文章\n2. 填写昵称、邮箱、评论内容\n3. 提交",
     "提示“评论正在等待审核”；前台不显示该评论；后台待审列表出现", "R04"),
    ("TC-COMM-002", "评论", "P0", "评论审核通过后才在前台展示",
     "状态迁移", "存在待审核评论",
     "1. 后台批准该评论\n2. 刷新前台页面",
     "前台评论列表出现该评论，显示昵称与内容", "R04"),
    ("TC-COMM-003", "评论", "P0", "评论内容中的脚本标签被转义",
     "错误推测/安全", "无",
     "1. 提交评论内容 <script>alert(1)</script>\n2. 后台批准\n3. 前台查看并观察是否弹窗",
     "内容以文本形式转义显示，不执行脚本、不弹窗", "R04"),
    ("TC-COMM-004", "评论", "P1", "管理员回复评论后的嵌套展示",
     "场景法", "存在已批准评论",
     "1. 后台对评论回复\n2. 前台查看评论区",
     "回复以嵌套层级显示在父评论下，作者标识正确", "R04"),
    ("TC-COMM-005", "评论", "P2", "将评论标记为垃圾后前台隐藏",
     "状态迁移", "存在已批准评论",
     "1. 后台标记为垃圾\n2. 刷新前台",
     "前台不再显示该评论；后台垃圾列表可见", "R04"),

    ("TC-API-001", "REST API", "P0", "未认证访问文章列表仅返回已发布内容",
     "接口测试", "站点已开启 REST API",
     "1. GET /wp-json/wp/v2/posts\n2. 检查返回条目状态",
     "返回 200；仅包含已发布文章；不含草稿/私密内容", "R05"),
    ("TC-API-002", "REST API", "P0", "使用应用密码认证后创建文章",
     "接口测试", "已生成 Application Password",
     "1. 使用 Basic Auth 认证\n2. POST /wp-json/wp/v2/posts 提交标题与内容\n3. GET 该文章",
     "返回 201；文章创建成功且状态符合请求", "R05"),
    ("TC-API-003", "REST API", "P0", "无发布权限角色调用创建文章接口",
     "接口测试/权限", "持有投稿者凭据",
     "1. 以投稿者身份 POST /wp-json/wp/v2/posts，status=publish",
     "返回 403 或文章被强制降为 pending；不得出现已发布文章", "R05"),
    ("TC-API-004", "REST API", "P1", "分页参数 per_page 的边界值",
     "边界值分析", "存在 120 篇以上文章",
     "1. 请求 per_page=1\n2. per_page=100\n3. per_page=101\n4. per_page=0",
     "1/100 正常返回；101 被限制为上限或返回 400；0 返回 400 或默认值，均不产生 500", "R05"),
    ("TC-API-005", "REST API", "P1", "非法参数返回结构化错误",
     "接口测试/异常", "无",
     "1. 请求 /wp-json/wp/v2/posts?status=not_a_status\n2. 请求不存在的文章 ID",
     "返回 400/404，响应体含 code 与 message 字段，不返回 HTML 错误页", "R05"),
    ("TC-API-006", "REST API", "P1", "未认证访问用户列表的信息暴露范围",
     "安全测试/信息泄露", "站点无额外加固插件",
     "1. 未认证 GET /wp-json/wp/v2/users\n2. 记录返回字段\n3. 与后台用户列表比对",
     "记录实际暴露字段（id/name/slug 等）；若暴露超出公开所需的信息，登记为信息泄露风险", "R05"),

    ("TC-PERM-001", "角色权限", "P0", "投稿者无法直接发布文章",
     "权限矩阵", "投稿者账号已创建",
     "1. 投稿者登录，新建文章\n2. 检查可用按钮\n3. 用其 Cookie+nonce 调 POST /wp-json/wp/v2/posts（status=publish）",
     "UI 仅有“提交审核”；接口返回 403 或强制 pending；无已发布文章产生", "R06"),
    ("TC-PERM-002", "角色权限", "P0", "订阅者无法进入后台功能页",
     "权限矩阵", "订阅者账号已创建",
     "1. 订阅者登录\n2. 直访 /wp-admin/edit.php\n3. 直访 /wp-admin/options-general.php",
     "均被拒绝或提示权限不足，不得进入列表页或设置页", "R06"),
    ("TC-PERM-003", "角色权限", "P0", "作者无法编辑他人文章（URL 直访）",
     "权限矩阵/越权", "存在作者 A 与其他作者 B 的文章",
     "1. 作者 A 登录\n2. 直访 /wp-admin/post.php?post={B的文章ID}&action=edit",
     "提示无权限或跳转，不得加载文章内容与编辑框", "R06"),
    ("TC-PERM-004", "角色权限", "P1", "编辑可审核评论但不能新建用户",
     "权限矩阵", "编辑账号已创建",
     "1. 编辑登录，直访 /wp-admin/edit-comments.php 并批准一条评论\n2. 直访 /wp-admin/user-new.php\n3. 调 POST /wp-json/wp/v2/users",
     "步骤 1 成功（正向对照）；步骤 2、3 被拒绝（403 或权限提示）", "R06"),
    ("TC-PERM-005", "角色权限", "P0", "作者通过接口删除他人文章被拒绝",
     "权限矩阵/接口越权", "持有作者 A 凭据与他人文章 ID",
     "1. DELETE /wp-json/wp/v2/posts/{他人ID}?force=true",
     "返回 403（rest_cannot_delete），文章仍存在", "R06"),

    ("TC-THEME-001", "外观与插件", "P2", "切换主题后前台正常渲染且无报错",
     "场景法", "已安装两个主题",
     "1. 后台切换主题\n2. 打开首页、文章页、搜索页\n3. 查看页面源代码是否有 PHP 警告",
     "三页均正常渲染，无白屏、无 PHP Warning/Notice 输出", "R07"),
    ("TC-PLUG-001", "外观与插件", "P2", "禁用插件后相关功能消失且站点正常",
     "回归测试", "已启用某插件（如缓存插件）",
     "1. 禁用插件\n2. 访问首页与后台\n3. 观察功能与报错",
     "插件功能入口消失；站点无白屏；后台无致命错误提示", "R07"),
    ("TC-PLUG-002", "外观与插件", "P2", "通过本地 zip 安装并启用插件",
     "场景法", "已下载插件 zip",
     "1. 插件→上传插件\n2. 选择 zip 安装\n3. 启用",
     "安装成功提示；插件出现在列表并可启用；启用后无冲突报错", "R07"),

    ("TC-SET-001", "系统设置", "P1", "修改站点标题后前台同步生效",
     "场景法", "已登录管理员",
     "1. 设置→常规，修改站点标题\n2. 保存\n3. 打开前台首页",
     "前台浏览器标题与页头同步更新；缓存开启时按缓存规则生效", "R08"),
    ("TC-SET-002", "系统设置", "P1", "修改固定链接结构后的旧链接行为",
     "边界值分析", "已存在多篇文章",
     "1. 将固定链接改为“文章名”\n2. 访问旧格式 URL\n3. 访问新格式 URL",
     "新链接可访问；旧链接按预期 301 或 404，不出现循环重定向", "R08"),
    ("TC-SET-003", "系统设置", "P1", "关闭评论后前台评论框消失、既有评论保留",
     "场景法", "存在已批准评论",
     "1. 设置→讨论，取消“允许发表评论”\n2. 打开文章页",
     "评论提交表单消失；既有评论仍展示（或按设置一并隐藏，需记录实际行为）", "R08"),

    ("TC-PERF-001", "性能与容量", "P0", "1000 篇文章下首页首屏响应时间基线",
     "性能测试", "已导入 1000 篇文章、未开启页面缓存",
     "1. 用 JMeter 以 10 并发压首页 5 分钟\n2. 记录 TPS、平均 RT、P95、错误率\n3. 开启 Redis Object Cache 后复压",
     "输出优化前后对比：TPS 提升 ≥50%，P95 下降 ≥30%；记录瓶颈定位结论", "R09"),

    ("TC-SEC-001", "安全防护", "P0", "缺少 nonce 的评论提交请求被拒绝",
     "安全测试/CSRF", "已登录普通用户",
     "1. 抓取正常评论提交请求\n2. 删除 _wpnonce 字段后重放\n3. 观察响应",
     "请求被拒绝（403 或校验失败提示），评论未被写入", "R10"),
]

PERM_ROLES = ["管理员", "编辑", "作者", "投稿者", "订阅者"]
PERM_OPS = ["OP1 发布文章", "OP2 编辑他人文章", "OP3 审核评论", "OP4 上传媒体", "OP5 新建用户", "OP6 修改设置"]
PERM = {
    "管理员": ["允许", "允许", "允许", "允许", "允许", "允许"],
    "编辑": ["允许", "允许", "允许", "允许", "拒绝", "拒绝"],
    "作者": ["仅自己", "拒绝", "拒绝", "允许", "拒绝", "拒绝"],
    "投稿者": ["拒绝(只能提交待审)", "拒绝", "拒绝", "拒绝", "拒绝", "拒绝"],
    "订阅者": ["拒绝", "拒绝", "拒绝", "拒绝", "拒绝", "拒绝"],
}

REQ = [
    ("R01", "登录与账号", "TC-AUTH-001 ~ TC-AUTH-005"),
    ("R02", "内容创作与发布流程", "TC-POST-001 ~ TC-POST-006"),
    ("R03", "媒体资源管理", "TC-MEDIA-001 ~ TC-MEDIA-005"),
    ("R04", "评论互动与审核", "TC-COMM-001 ~ TC-COMM-005"),
    ("R05", "REST API 可用性与鉴权", "TC-API-001 ~ TC-API-006"),
    ("R06", "角色与权限控制", "TC-PERM-001 ~ TC-PERM-005"),
    ("R07", "外观与插件管理", "TC-THEME-001, TC-PLUG-001, TC-PLUG-002"),
    ("R08", "系统设置", "TC-SET-001 ~ TC-SET-003"),
    ("R09", "性能与容量", "TC-PERF-001"),
    ("R10", "安全防护", "TC-SEC-001"),
]

ENV = [
    ("被测系统", "WordPress 6.6.x（固定 tag，禁用 latest）"),
    ("数据库", "MariaDB 11"),
    ("缓存", "Redis 7 + Redis Object Cache 插件"),
    ("Web 服务器", "Apache（官方镜像内置）"),
    ("操作系统", "Windows 11 + WSL2 / Docker Desktop"),
    ("浏览器", "Chrome 最新版、Edge 最新版、Firefox 最新版"),
    ("分辨率", "1366×768、1920×1080"),
    ("自动化", "Selenium 4 + TestNG 7 + Maven 3.9 + Allure 2.x"),
    ("接口测试", "Postman + Newman"),
    ("性能测试", "Apache JMeter 5.6.3"),
    ("安全测试", "OWASP ZAP 2.15+"),
    ("缺陷管理", "禅道（开源版）或 GitHub Issues"),
    ("持续集成", "GitHub Actions"),
    ("大模型", "DeepSeek deepseek-chat / deepseek-reasoner；对照 Qwen2.5-Coder"),
]


def style_header(ws, row=1, ncols=None):
    ncols = ncols or ws.max_column
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = CENTER
        cell.border = BORDER


def main():
    wb = Workbook()

    # ---------- 说明 ----------
    ws = wb.active
    ws.title = "说明"
    ws["A1"] = "WordPress Web 测试 · 核心 40 条测试用例"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:D1")
    info = [
        ("项目", "基于 DeepSeek 的开源 CMS 系统 Web 测试与质量评估——以 WordPress 为例"),
        ("文档编号", "TC-WP-2026-001"),
        ("版本", "V1.0"),
        ("用例总数", f"{len(CASES)} 条（本表为核心集，完整集 120 条）"),
        ("设计方法", "等价类、边界值、判定表、状态迁移、场景法、错误推测、权限矩阵"),
        ("使用说明", "执行后请在“测试用例”表填写“执行结果/实际结果/缺陷ID/执行人/执行日期”五列；执行结果下拉选择。"),
        ("归因规则", "任何非“通过”用例必须先填写“归因”，取值为 环境问题 / 脚本问题 / 系统缺陷；仅“系统缺陷”才登记缺陷单。"),
    ]
    r = 3
    for k, v in info:
        ws.cell(row=r, column=1, value=k).font = Font(name="微软雅黑", size=10, bold=True)
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor="DDEBF7")
        ws.cell(row=r, column=1).border = BORDER
        ws.cell(row=r, column=2, value=v).font = BODY_FONT
        ws.cell(row=r, column=2).alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        ws.cell(row=r, column=2).border = BORDER
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="统计").font = TITLE_FONT
    r += 1
    pr = Counter(c[2] for c in CASES)
    mod = Counter(c[1] for c in CASES)
    met = Counter(c[4] for c in CASES)
    stats = [("优先级分布", "，".join(f"{k}: {v} 条" for k, v in sorted(pr.items()))),
             ("模块分布", "，".join(f"{k}: {v} 条" for k, v in mod.items())),
             ("方法分布", "，".join(f"{k}: {v} 条" for k, v in met.most_common()))]
    for k, v in stats:
        ws.cell(row=r, column=1, value=k).font = Font(name="微软雅黑", size=10, bold=True)
        ws.cell(row=r, column=2, value=v).font = BODY_FONT
        ws.cell(row=r, column=2).alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        r += 1

    ws.column_dimensions["A"].width = 14
    for col in "BCD":
        ws.column_dimensions[col].width = 30

    # ---------- 测试用例 ----------
    ws2 = wb.create_sheet("测试用例")
    headers = ["用例ID", "模块", "优先级", "用例标题", "设计方法", "前置条件",
               "操作步骤", "预期结果", "需求ID", "执行结果", "实际结果", "归因", "缺陷ID", "执行人", "执行日期"]
    ws2.append(headers)
    for c in CASES:
        ws2.append(list(c) + ["未执行", "", "", "", "", ""])
    widths = [14, 12, 8, 34, 16, 26, 42, 42, 9, 10, 26, 12, 10, 9, 12]
    for i, w in enumerate(widths, start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    style_header(ws2)
    for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row, max_col=len(headers)):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = WRAP
        row[2].alignment = CENTER
        row[8].alignment = CENTER
        row[9].alignment = CENTER
    ws2.freeze_panes = "D2"
    ws2.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws2.max_row}"

    dv1 = DataValidation(type="list", formula1='"未执行,通过,失败,阻塞"', allow_blank=True)
    dv2 = DataValidation(type="list", formula1='"环境问题,脚本问题,系统缺陷"', allow_blank=True)
    ws2.add_data_validation(dv1)
    ws2.add_data_validation(dv2)
    dv1.add(f"J2:J{ws2.max_row}")
    dv2.add(f"L2:L{ws2.max_row}")

    # ---------- 权限矩阵 ----------
    ws3 = wb.create_sheet("权限矩阵")
    ws3["A1"] = "5 角色 × 6 操作 权限矩阵（预期）"
    ws3["A1"].font = TITLE_FONT
    ws3.merge_cells("A1:H1")
    ws3.append([])
    ws3.append(["角色"] + PERM_OPS + ["说明"])
    for role in PERM_ROLES:
        ws3.append([role] + PERM[role] + [""])
    ws3.cell(row=7, column=1, value="验证方法").font = Font(name="微软雅黑", size=10, bold=True)
    notes = [
        "每格须双通道验证：通道A 用该角色登录看 UI；通道B 复制其 Cookie+nonce 直接请求接口/URL。",
        "只有通道B 也被拒绝，才判定“权限控制有效”；否则记为 P0 权限绕过缺陷。",
        "必须保留至少 1 条正向对照（如编辑可审核评论），防止环境整体降权造成假通过。",
        "期望允许 9 格（含 1 格“仅自己”），期望拒绝 21 格。",
    ]
    for i, t in enumerate(notes, start=8):
        ws3.cell(row=i, column=1, value=t).font = BODY_FONT
        ws3.merge_cells(start_row=i, start_column=1, end_row=i, end_column=7)
    ws3.column_dimensions["A"].width = 14
    for i in range(2, 9):
        ws3.column_dimensions[get_column_letter(i)].width = 20
    for c in range(1, 8):
        cell = ws3.cell(row=3, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = CENTER
        cell.border = BORDER
    for r_ in range(4, 9):
        for c in range(1, 8):
            cell = ws3.cell(row=r_, column=c)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = CENTER

    # ---------- 需求追溯 ----------
    ws4 = wb.create_sheet("需求追溯")
    ws4.append(["需求ID", "需求描述", "覆盖用例", "用例数", "覆盖率"])
    cnt = Counter(c[8] for c in CASES)
    for rid, desc, cases in REQ:
        ws4.append([rid, desc, cases, cnt.get(rid, 0), "100%"])
    for i, w in enumerate([10, 30, 34, 10, 10], start=1):
        ws4.column_dimensions[get_column_letter(i)].width = w
    style_header(ws4)
    for row in ws4.iter_rows(min_row=2, max_row=ws4.max_row, max_col=5):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = WRAP
        row[0].alignment = CENTER
        row[3].alignment = CENTER
        row[4].alignment = CENTER

    # ---------- 环境与工具 ----------
    ws5 = wb.create_sheet("环境与工具")
    ws5.append(["类别", "配置/版本"])
    for k, v in ENV:
        ws5.append([k, v])
    ws5.column_dimensions["A"].width = 16
    ws5.column_dimensions["B"].width = 60
    style_header(ws5)
    for row in ws5.iter_rows(min_row=2, max_row=ws5.max_row, max_col=2):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = WRAP

    # ---------- 缺陷记录 ----------
    ws6 = wb.create_sheet("缺陷记录")
    ws6.append(["缺陷ID", "标题", "所属模块", "关联用例", "严重等级", "优先修复",
                "复现步骤", "期望结果", "实际结果", "归因", "状态", "截图/附件", "发现日期", "关闭日期"])
    ws6.append(["DEF-001", "（示例）示例缺陷，填写后删除", "M6 角色权限", "TC-PERM-001", "P0", "是",
                "1. 以投稿者身份调用创建文章接口并指定 status=publish", "返回 403 或降级为 pending",
                "文章被直接发布", "系统缺陷", "待修复", "shot-001.png", "2026-12-05", ""])
    for i, w in enumerate([10, 30, 12, 14, 9, 9, 40, 30, 30, 10, 9, 14, 12, 12], start=1):
        ws6.column_dimensions[get_column_letter(i)].width = w
    style_header(ws6)
    for row in ws6.iter_rows(min_row=2, max_row=ws6.max_row, max_col=14):
        for cell in row:
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = WRAP
    dv3 = DataValidation(type="list", formula1='"P0,P1,P2,P3"', allow_blank=True)
    dv4 = DataValidation(type="list", formula1='"待修复,修复中,已修复,已关闭,不予修复"', allow_blank=True)
    ws6.add_data_validation(dv3)
    ws6.add_data_validation(dv4)
    dv3.add("E2:E200")
    dv4.add("K2:K200")

    wb.save(OUT)
    print("saved:", OUT)
    print("cases:", len(CASES), "| priorities:", dict(sorted(Counter(c[2] for c in CASES).items())))


if __name__ == "__main__":
    main()
