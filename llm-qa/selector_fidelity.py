import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "outputs")

# 被测系统真实存在的定位器（来自我们的 Page Object 与页面实测）
REAL = {
    "user_login", "user_pass", "wp-submit", "login_error",
    "title", "save-post", "publish", "message", "wpadminbar",
    "comment", "author", "email", "submit", "wpbody",
}
# 输入里明确给出过的选择器（上下文遵循度）
GIVEN = {"user_login", "user_pass", "wp-submit", "login_error", "title",
         "save-post", "publish", "comment", "author", "email", "submit"}

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')


def extract_ids(code):
    ids = ID_PAT.findall(code)
    for css in CSS_PAT.findall(code):
        ids.extend(re.findall(r'#([A-Za-z0-9_-]+)', css))
    return ids


rows = []
for d in sorted(glob.glob(os.path.join(OUT, "cmp-*"))):
    model = os.path.basename(d).replace("cmp-", "")
    total = real = given = 0
    for f in glob.glob(os.path.join(d, "scripts", "*.java")):
        code = open(f, encoding="utf-8", errors="replace").read()
        ids = extract_ids(code)
        total += len(ids)
        real += sum(1 for i in ids if i in REAL)
        given += sum(1 for i in ids if i in GIVEN)
    rows.append({
        "model": model,
        "selectors": total,
        "real": real,
        "given": given,
        "fidelity": round(real / total * 100, 1) if total else 0,
        "context": round(given / total * 100, 1) if total else 0,
    })

print(f"{'模型':<26}{'定位器总数':>10}{'命中真实':>10}{'命中率':>9}{'落在给定上下文':>14}")
for r in rows:
    print(f"{r['model']:<26}{r['selectors']:>10}{r['real']:>10}{r['fidelity']:>8.1f}%{r['context']:>13.1f}%")

with open(os.path.join(OUT, "selector-fidelity.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=2)
print("\n已写入 outputs/selector-fidelity.json")
