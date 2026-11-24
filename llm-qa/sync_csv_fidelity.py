# -*- coding: utf-8 -*-
"""把 n=10 的定位器保真度同步进 metrics-v2.csv。"""

import csv
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
f10 = {r["model"]: r["fidelity"]
       for r in json.load(open(os.path.join(BASE, "outputs", "selector-fidelity10.json"),
                               encoding="utf-8"))}

path = os.path.join(BASE, "outputs", "metrics-v2.csv")
rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
for r in rows:
    if r["模型"] in f10:
        r["定位器保真度"] = f"{f10[r['模型']]}%"

with open(path, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print([(r["模型"], r["定位器保真度"]) for r in rows])
