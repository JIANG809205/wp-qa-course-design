# -*- coding: utf-8 -*-
"""当 github.com 的 git 端口不可达时，改用 GitHub REST API 提交并更新分支。"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.request

OWNER, REPO = "JIANG809205", "wp-qa-course-design"
BRANCH = "master"
ROOT = r"E:\软件质量保证与测试课程设计"
GH = r"C:\Program Files\GitHub CLI\gh.exe"

token = subprocess.run([GH, "auth", "token"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
if not token:
    raise SystemExit("拿不到 token")


def api(method: str, path: str, payload=None):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


# 1) 当前远程 HEAD
ref = api("GET", f"/git/ref/heads/{BRANCH}")
parent_sha = ref["object"]["sha"]
base_commit = api("GET", f"/git/commits/{parent_sha}")
base_tree = base_commit["tree"]["sha"]
print("远程 HEAD:", parent_sha[:7])

# 2) 本地相对远程变更的文件
out = subprocess.run(["git", "diff", "--name-only", f"{parent_sha}", "HEAD"],
                     cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
files = [f.strip() for f in out.splitlines() if f.strip()]
print(f"变更文件 {len(files)} 个")

entries = []
for rel in files:
    full = os.path.join(ROOT, rel)
    if not os.path.exists(full):
        entries.append({"path": rel.replace("\\", "/"), "mode": "100644",
                        "type": "blob", "sha": None})
        continue
    raw = open(full, "rb").read()
    try:
        text = raw.decode("utf-8")
        blob = api("POST", "/git/blobs", {"content": text, "encoding": "utf-8"})
    except UnicodeDecodeError:
        blob = api("POST", "/git/blobs",
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
    entries.append({"path": rel.replace("\\", "/"), "mode": "100644",
                    "type": "blob", "sha": blob["sha"]})
    print("  上传", rel)

# 3) 建树
tree = api("POST", "/git/trees", {"base_tree": base_tree, "tree": entries})
print("新 tree:", tree["sha"][:7])

# 4) 建提交
msg = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=ROOT,
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
commit = api("POST", "/git/commits",
             {"message": msg or "update", "tree": tree["sha"], "parents": [parent_sha]})
print("新 commit:", commit["sha"][:7])

# 5) 更新分支
api("PATCH", f"/git/refs/heads/{BRANCH}", {"sha": commit["sha"], "force": False})
print("✅ 已通过 API 推送到远程 master")
