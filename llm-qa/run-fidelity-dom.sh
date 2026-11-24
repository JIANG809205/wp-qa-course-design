#!/bin/bash
# 校验 dom-ids.json 并重算保真度
cd "/mnt/e/软件质量保证与测试课程设计/llm-qa" || exit 1
/opt/qa-venv/bin/python - <<'PY'
import json
d = json.load(open("data/dom-ids.json", encoding="utf-8"))
print("字段:", list(d.keys()))
print("id:", len(d.get("ids", [])), "name:", len(d.get("names", [])),
      "class:", len(d.get("classes", [])))
PY
echo "--- 保真度 ---"
/opt/qa-venv/bin/python selector_fidelity_dom.py
