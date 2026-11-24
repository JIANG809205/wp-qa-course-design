# -*- coding: utf-8 -*-
"""打包提交物：排除密钥、日志、大体积中间产物；生成代码包与附录包两个 zip。"""

from __future__ import annotations

import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))

# 绝不进包的内容
DENY_NAMES = {".env", ".env.local", "wordpress-7.1.5.zip", "wp-cli.phar"}
DENY_DIRS = {"node_modules", ".git", "__pycache__", ".pytest_cache", "target", "screenshots-raw"}
DENY_SUFFIX = (".log", ".jtl", ".phar", ".pyc")
DENY_PREFIX = ("_", "diag", "debug_")

CODE_ZIP = os.path.join(ROOT, "提交物-课程设计代码.zip")
DATA_ZIP = os.path.join(ROOT, "附录-原始数据.zip")


def denied(rel: str, name: str) -> bool:
    parts = rel.split(os.sep)
    if name in DENY_NAMES:
        return True
    if any(p in DENY_DIRS for p in parts):
        return True
    if name.endswith(DENY_SUFFIX) or name.startswith(DENY_PREFIX):
        return True
    return False


def build(zip_path: str, keep, max_size: int) -> tuple[int, int]:
    count = skipped = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in DENY_DIRS]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT)
                if denied(rel, fn) or not keep(rel):
                    skipped += 1
                    continue
                try:
                    if os.path.getsize(full) > max_size:
                        skipped += 1
                        continue
                    zf.write(full, rel)
                    count += 1
                except OSError:
                    skipped += 1
    return count, skipped


def is_code(rel: str) -> bool:
    return not rel.startswith(("wp-perf/results-rigor", "wp-compat/screenshots",
                               "llm-qa/outputs/rigor", "wp-autotest/result"))


def is_data(rel: str) -> bool:
    return rel.endswith((".json", ".csv", ".md", ".png", ".xlsx", ".jtl"))


if __name__ == "__main__":
    c, cs = build(CODE_ZIP, is_code, 8 * 1024 * 1024)
    print(f"代码包: {c} 个文件，跳过 {cs} 个，{os.path.getsize(CODE_ZIP)//1024} KB")
    d, ds = build(DATA_ZIP, is_data, 12 * 1024 * 1024)
    print(f"附录包: {d} 个文件，跳过 {ds} 个，{os.path.getsize(DATA_ZIP)//1024} KB")

    # 自检：确认密钥不在包里
    with zipfile.ZipFile(CODE_ZIP) as zf:
        names = zf.namelist()
        bad = [n for n in names if n.endswith(".env") or "_" == os.path.basename(n)[:1]
               or n.endswith(".log")]
        print("含敏感/日志文件:", bad or "无")
        print("包内顶层目录:", sorted({n.split('/')[0] for n in names})[:12])
