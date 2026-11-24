# -*- coding: utf-8 -*-
"""把 10 条缺陷写入用例工作簿的「缺陷记录」表，并回填用例执行状态。"""

import datetime
import os

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05-测试用例-核心40条.xlsx")
TODAY = "2026-11-23"

DEFECTS = [
    # id, 标题, 模块, 关联用例, 等级, 优先修复, 步骤, 期望, 实际, 归因, 状态
    ("DEF-001", "登录无失败次数限制，可无限次尝试", "M1 登录与账号", "TC-AUTH-005", "P1", "是",
     "1.打开 /wp-login.php 2.用户名 admin、密码填错 3.连续提交 6 次", "达到阈值后出现验证码/锁定/429",
     "6 次均返回 200，始终提示密码不正确，无任何限制", "系统缺陷", "待修复"),
    ("DEF-002", "调试日志 debug.log 可被匿名下载", "M8 系统设置", "探索性测试", "P1", "是",
     "GET /wp-content/debug.log", "403/404", "HTTP 200，返回 4437 字节，含 /var/www/html 绝对路径与数据库报错",
     "系统缺陷", "待修复"),
    ("DEF-003", "上传目录开启目录浏览", "M3 媒体库", "探索性测试", "P2", "是",
     "GET /wp-content/uploads/", "403/404", "HTTP 200，页面标题“Index of /wp-content/uploads”", "系统缺陷", "待修复"),
    ("DEF-004", "缺少安全响应头", "M10 安全防护", "探索性测试", "P2", "否",
     "curl -I http://localhost:8080/", "含 X-Frame-Options 等 4 项",
     "X-Frame-Options、X-Content-Type-Options、Referrer-Policy、Permissions-Policy 全部缺失", "系统缺陷", "待修复"),
    ("DEF-005", "XML-RPC 接口开放", "M10 安全防护", "探索性测试", "P2", "否",
     "POST /xmlrpc.php，body 为 system.listMethods", "关闭（403/404）", "HTTP 200，返回 methodResponse 与方法列表",
     "系统缺陷", "待修复"),
    ("DEF-006", "未认证可枚举用户信息", "M5 REST API", "TC-API-006", "P2", "是",
     "未登录 GET /wp-json/wp/v2/users", "401/403 或仅最小字段",
     "HTTP 200，返回 5 个用户，含 id/name/slug/url/avatar_urls", "系统缺陷", "待修复"),
    ("DEF-007", "评论洪水保护对正常用户误伤", "M4 评论", "TC-COMM-001", "P2", "否",
     "提交第 1 条评论成功后，间隔数秒提交第 2 条", "第 2 条正常进入待审核",
     "提示“您提交评论的速度太快了”，评论未被接收", "系统缺陷", "待修复"),
    ("DEF-008", "上传空文件返回 500 而非 4xx", "M3 媒体库", "TC-MEDIA-005", "P3", "否",
     "POST /wp-json/wp/v2/media 上传 0 字节 png", "4xx 且提示文件为空",
     "HTTP 500，rest_upload_unknown_error", "系统缺陷", "待修复"),
    ("DEF-009", "超限上传错误码与提示不准确", "M3 媒体库", "TC-MEDIA-002", "P3", "否",
     "上传 20MB 图片（上限 16MB）", "提示超过大小限制且错误码一致",
     "HTTP 400，错误码 rest_upload_no_content_disposition", "系统缺陷", "待修复"),
    ("DEF-010", "Server 响应头暴露具体版本", "M10 安全防护", "探索性测试", "P3", "否",
     "curl -I http://localhost:8080/", "仅返回 Server: Apache 或隐藏版本", "Server: Apache/2.4.52 (Ubuntu)",
     "系统缺陷", "待修复"),
]

# 用例执行状态回填（含失败与缺陷关联）
CASE_RESULT = {
    "TC-AUTH-005": ("失败", "连续 6 次错误密码均可继续尝试，无锁定", "系统缺陷", "DEF-001"),
    "TC-API-006": ("失败", "未认证 /users 返回 5 个用户及 id/slug/avatar 等字段", "系统缺陷", "DEF-006"),
    "TC-MEDIA-002": ("失败", "20MB 上传返回 400，但错误码与提示不指向大小限制", "系统缺陷", "DEF-009"),
    "TC-MEDIA-005": ("失败", "0 字节上传返回 500 rest_upload_unknown_error", "系统缺陷", "DEF-008"),
}

wb = openpyxl.load_workbook(XLSX)

# ---------- 缺陷记录 ----------
ws = wb["缺陷记录"]
# 清空旧数据（保留表头）
if ws.max_row > 1:
    ws.delete_rows(2, ws.max_row - 1)

head_font = Font(name="微软雅黑", size=10)
red = PatternFill("solid", fgColor="FFC7CE")
warn = PatternFill("solid", fgColor="FFEB9C")
wrap = Alignment(vertical="center", wrap_text=True)

for i, d in enumerate(DEFECTS, start=2):
    row = [d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], "见截图", TODAY, ""]
    for c, v in enumerate(row, start=1):
        cell = ws.cell(row=i, column=c, value=v)
        cell.font = head_font
        cell.alignment = wrap
    lvl = ws.cell(row=i, column=5)
    lvl.fill = red if d[4] == "P1" else (warn if d[4] == "P2" else PatternFill())

# ---------- 用例执行状态 ----------
ws2 = wb["测试用例"]
headers = [c.value for c in ws2[1]]
idx = {name: i + 1 for i, name in enumerate(headers)}
updated = 0
for r in range(2, ws2.max_row + 1):
    cid = ws2.cell(row=r, column=idx["用例ID"]).value
    if cid in CASE_RESULT:
        status, actual, cause, did = CASE_RESULT[cid]
        ws2.cell(row=r, column=idx["执行结果"], value=status).fill = red
        ws2.cell(row=r, column=idx["实际结果"], value=actual)
        ws2.cell(row=r, column=idx["归因"], value=cause)
        ws2.cell(row=r, column=idx["缺陷ID"], value=did)
        ws2.cell(row=r, column=idx["执行人"], value="手工+自动化")
        ws2.cell(row=r, column=idx["执行日期"], value=TODAY)
        updated += 1

# ---------- 汇总表 ----------
if "缺陷汇总" in wb.sheetnames:
    del wb["缺陷汇总"]
s = wb.create_sheet("缺陷汇总")
s.append(["等级", "数量", "缺陷编号"])
s.append(["P1 严重", 2, "DEF-001、DEF-002"])
s.append(["P2 一般", 5, "DEF-003 ~ DEF-007"])
s.append(["P3 轻微", 3, "DEF-008 ~ DEF-010"])
s.append(["合计", 10, ""])
s.append([])
s.append(["缺陷有效率", "10/10（均复现两次以上，无脚本/环境误判）"])
for i, w in enumerate([14, 8, 40], start=1):
    s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for cell in s[1]:
    cell.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F4E79")

wb.save(XLSX)
print(f"缺陷写入 {len(DEFECTS)} 条，用例状态回填 {updated} 条")
