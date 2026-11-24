import csv
import json
import os

BASE = "/mnt/e/软件质量保证与测试课程设计/llm-qa"
v2 = json.load(open(os.path.join(BASE, "outputs", "metrics-v2.json"), encoding="utf-8"))
tri = json.load(open(os.path.join(BASE, "outputs", "triage-hard.json"), encoding="utf-8"))

NAME = {"deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
        "deepseek-v4-pro": "DeepSeek-V4-Pro",
        "qwen-plus": "Qwen-Plus"}

tri_acc = {}
tri_wrong = {}
for r in tri["rows"]:
    tri_acc[r["model"]] = r["accuracy"]
    tri_wrong[r["model"]] = sum(1 for d in r["detail"]
                                if d["gold"] != "系统缺陷" and d["got"] == "系统缺陷")

rows = []
for r in v2["rows"]:
    label = NAME.get(r["model"], r["model"])
    rows.append({
        "模型": label,
        "用例数": r["cases"],
        "严格结构合规率": f"{r['strict_rate']}%",
        "需求点覆盖率": f"{r['coverage']}%",
        "定位器保真度": f"{r['selector_fidelity']}%",
        "URL 错误脚本数": f"{r['url_bad_scripts']}/{r['scripts']}",
        "可直接运行率": f"{r['runnable_rate']}%",
        "归因准确率(12难样本)": f"{tri_acc.get(label, '-')}%",
        "误判为缺陷次数": tri_wrong.get(label, "-"),
    })

out = os.path.join(BASE, "outputs", "metrics-v2.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(out)
for r in rows:
    print(" | ".join(f"{k}={v}" for k, v in r.items()))
