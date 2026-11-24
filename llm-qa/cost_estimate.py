# -*- coding: utf-8 -*-
"""按"样本均值 × 实际调用次数"估算 token 消耗（标注为估算）。"""

from __future__ import annotations

import glob
import json
import os
import statistics

CHARS_PER_TOKEN = 2.0
PROMPT_CHARS = 300

# 每个模型实际调用次数（cases + scripts + triage）
CALLS = {
    "DeepSeek-V4.1-Flash": {"cases": 20 * 3, "scripts": 10, "triage": 24},
    "DeepSeek-V4-Pro": {"cases": 20, "scripts": 10, "triage": 24},
    "Qwen-Plus": {"cases": 20, "scripts": 10, "triage": 24},
}

SAMPLE = {
    "DeepSeek-V4.1-Flash": ["/mnt/e/软件质量保证与测试课程设计/llm-qa/outputs/rigor/cases/rep1/*.json",
                            "/opt/qa/scripts10/deepseek-v4.1-flash/*.java"],
    "DeepSeek-V4-Pro": ["/opt/qa/rigor-pro/cases/rep1/*.json",
                        "/opt/qa/scripts10/deepseek-v4-pro/*.java"],
    "Qwen-Plus": ["/opt/qa/rigor-qwen/cases/rep1/*.json",
                  "/opt/qa/scripts10/qwen-plus/*.java"],
}

rows = []
for model, patterns in SAMPLE.items():
    sizes = []
    for p in patterns:
        for f in glob.glob(p):
            try:
                sizes.append(len(open(f, encoding="utf-8", errors="replace").read()))
            except OSError:
                pass
    if not sizes:
        print(f"{model}: 无样本，跳过")
        continue
    avg_out = statistics.mean(sizes)
    calls = sum(CALLS[model].values())
    tokens = int(calls * (avg_out + PROMPT_CHARS) / CHARS_PER_TOKEN)
    rows.append({"model": model, "sample_files": len(sizes), "avg_output_chars": int(avg_out),
                 "calls": calls, "tokens_est": tokens})
    print(f"{model:<22} 样本 {len(sizes):>2} 个，平均输出 {int(avg_out):>5} 字符，"
          f"调用 {calls:>3} 次 → 约 {tokens:>7,} tokens")

total = sum(r["tokens_est"] for r in rows)
print(f"\n合计约 {total:,} tokens（估算：调用次数 ×（平均输出 + 300 字符提示词）/ 2.0）")
print("说明：非 API 返回的 usage，仅作量级参考；实际计费以供应商账单为准。")

out = "/mnt/e/软件质量保证与测试课程设计/llm-qa/outputs/cost-estimate.json"
json.dump({"rows": rows, "total_tokens_est": total,
           "method": "调用次数 ×（平均输出字符 + 300）/ 2.0"},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已写入", out)
