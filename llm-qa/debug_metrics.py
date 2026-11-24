import glob
import os
import re
import sys

sys.path.insert(0, "/mnt/e/软件质量保证与测试课程设计/llm-qa")
from evaluate_v2 import strip_comments, url_correct, assertion_strength  # noqa: E402

CLASS_RE = re.compile(r"\bclass\s+\w+")

for d in sorted(glob.glob("/mnt/e/软件质量保证与测试课程设计/llm-qa/outputs/cmp-*")):
    model = os.path.basename(d).replace("cmp-", "")
    for f in sorted(glob.glob(os.path.join(d, "scripts", "*.java"))):
        code = open(f, encoding="utf-8", errors="replace").read()
        body = strip_comments(code)
        urls = re.findall(r"https?://[^\s\"')]+", body)
        ok = url_correct(code)
        has_class = bool(CLASS_RE.search(body))
        asserts = assertion_strength(code)["asserts"]
        print(f"{model:<24}{os.path.basename(f):<18} url_ok={str(ok):<6} urls={urls[:2]} asserts={asserts} class={has_class}")
