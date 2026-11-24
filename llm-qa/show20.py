import glob
import json

for f in sorted(glob.glob("/opt/qa/scripts20-*/scripts20-summary.json")):
    d = json.load(open(f, encoding="utf-8"))[0]
    lo, hi = d["runnable_ci"]
    print(f"{d['model']:<22} n={d['n']}  可运行 {d['runnable_k']}/{d['n']} = {d['runnable_rate']}%  "
          f"CI [{lo:.0f}%, {hi:.0f}%]  有类 {d['class_rate']}%  URL {d['url_ok_rate']}%")
