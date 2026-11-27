# -*- coding: utf-8 -*-
"""生成答辩记录填写稿副本（原空白表保留不动）。"""

import shutil

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

SRC = r"E:\软件质量保证与测试课程设计\答辩记录-学号-姓名 (1).docx"
OUT = r"E:\软件质量保证与测试课程设计\答辩记录-241303109-蒋晓涵.docx"

shutil.copyfile(SRC, OUT)
doc = Document(OUT)

STUDENT = {"学号": "241303109", "专业": "软件工程", "姓名": "蒋晓涵", "班级": "软件2401"}

TOPIC = (
    "课题名称、主要目标和具体要求：\n"
    "1.课题名称：基于大模型的开源CMS系统（WordPress）Web测试\n"
    "2.主要目标：\n"
    "掌握Web测试概念、流程和方法；深入理解大模型在Web测试中的应用方式与局限；"
    "熟悉Selenium、pytest、JMeter等自动化与性能测试工具；能够针对实际Web应用设计并执行有效的测试方案；"
    "通过测试数据分析识别问题并为质量改进提供建议。\n"
    "3.具体要求：\n"
    "设计并执行针对WordPress的完整Web测试，覆盖功能、接口、权限、性能、安全与兼容性；"
    "引入大模型完成需求到用例、用例到脚本、失败日志归因三项任务，"
    "并以结构合规率、定位器保真度、可运行率、归因准确率等指标量化大模型产出的真实可用性；"
    "提交测试计划、测试用例、缺陷清单与课程设计报告。\n"
    "4.进程安排：\n"
    "2026年11月—12月，共4周：第1周开题与环境搭建；第2周功能与接口测试；"
    "第3周性能与安全测试；第4周大模型评测与报告撰写。"
)

QA = (
    "答辩记录：\n"
    "问题1：为什么选择WordPress而不是自研系统作为被测对象？\n"
    "答：WordPress是真实在用的生产级开源CMS（全球约43%的网站使用），缺陷具有现实意义；官方提供完整安装包与文档，"
    "版本和数据可以固定——本次用官方checksum接口核对了3783个文件全部一致，任何人按文档可复现同一环境；"
    "同时能取得请求—响应—服务端日志的完整证据链，自研系统做不到这一点。\n"
    "\n"
    "问题2：大模型生成脚本的严格可运行率只有5.2%，这个数字说明什么？\n"
    "答：这是96条样本上带95%置信区间（2.2%–11.6%）的结果。同一批脚本的结构可运行率有64.6%，"
    "但以真实DOM（1181个id、193个name、769个class）为基准时定位器只有29%真实存在——差距就是定位器幻觉的量化。"
    "结论是大模型产出的测试资产必须经过可执行性校验才能进工程；另外Qwen定位器保真度最高却完全不输出类声明，"
    "一行都编译不过，说明单一指标不能替代整体可用性判断。\n"
    "\n"
    "问题3：列表页100并发时P95达2834毫秒，瓶颈在哪里，怎么验证的？\n"
    "答：瓶颈是CPU。压测期间容器CPU稳定在590%–680%，相当于8核中占6–6.8核，而TPS不随并发增长。"
    "做了两次优化实验均为负结果：调大Apache workers和InnoDB缓冲池后吞吐几乎不变，说明瓶颈不在连接数或缓冲池；"
    "启用mod_cache后缓存目录只有4K，因为响应带Vary: Cookie头不命中。所以优化方向是横向扩容和治理Cookie与缓存头，"
    "而不是调这些参数。\n"
    "\n"
    "答辩人：蒋晓涵                                   日期：2026年12月"
)


def set_cell(cell, text, size=10.5):
    cell.text = ""
    for i, ln in enumerate(text.split("\n")):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(ln)
        r.font.size = Pt(size)
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def fill_kv(tb, key, value):
    """在表格中找到 key 所在单元格，填右侧相邻单元格。"""
    for row in tb.rows:
        cells = list(dict.fromkeys(row.cells))
        for i, c in enumerate(cells):
            if c.text.strip() == key and i + 1 < len(cells):
                set_cell(cells[i + 1], value)
                return True
    return False


# --- 表0：头信息与课题内容 ---
tb0 = doc.tables[0]
for k, v in STUDENT.items():
    fill_kv(tb0, k, v)
for row in tb0.rows:
    merged = list(dict.fromkeys(row.cells))
    if len(merged) == 1 and merged[0].text.strip().startswith("课题名称"):
        set_cell(merged[0], TOPIC)

# --- 表1：信息与答辩记录 ---
tb1 = doc.tables[1]
for k, v in STUDENT.items():
    fill_kv(tb1, k, v)
for row in tb1.rows:
    merged = list(dict.fromkeys(row.cells))
    big = merged[-1]
    if "答辩记录" in big.text and "问题1" in big.text:
        set_cell(big, QA)

doc.save(OUT)
print("已生成:", OUT)
