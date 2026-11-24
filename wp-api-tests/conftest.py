"""pytest 公共配置：鉴权、被测地址、结果落盘。"""

from __future__ import annotations

import json
import os

import pytest
import requests

BASE = os.getenv("WP_BASE", "http://localhost:8080")
PASS_DIR = "/tmp/wp_pass"
ROLES = ["admin", "editor", "author", "contributor", "subscriber"]

RESULTS: list[dict] = []


def _read_pass(role: str) -> str:
    path = os.path.join(PASS_DIR, f"{role}.txt")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read().strip()
    return ""


@pytest.fixture(scope="session")
def base() -> str:
    return BASE


@pytest.fixture(scope="session")
def tokens() -> dict[str, str]:
    return {r: _read_pass(r) for r in ROLES}


@pytest.fixture(scope="session")
def api() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "qa-pytest/1.0"})
    return s


@pytest.fixture(scope="session")
def admin(tokens) -> requests.Session:
    s = requests.Session()
    s.auth = ("admin", tokens["admin"])
    s.headers.update({"User-Agent": "qa-pytest/1.0"})
    return s


@pytest.fixture(scope="session")
def anon() -> requests.Session:
    return requests.Session()


import re

CASE_RE = re.compile(r"test_(TC)_([A-Z]+)_(\d{3})_")


def pytest_runtest_logreport(report):
    """把每个用例的结果记录下来，供 Excel 回填使用。"""
    if report.when != "call" and not (report.when == "setup" and report.failed):
        return
    case_id = ""
    m = CASE_RE.search(report.nodeid)
    if m:
        case_id = f"TC-{m.group(2)}-{m.group(3)}"
    RESULTS.append({
        "nodeid": report.nodeid,
        "case": case_id,
        "outcome": "passed" if report.passed else ("failed" if report.failed else "skipped"),
        "duration": round(report.duration, 2),
        "detail": (report.longreprtext or "")[-400:] if report.failed else "",
    })


def pytest_sessionfinish(session, exitstatus):
    path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(RESULTS, fh, ensure_ascii=False, indent=2)
    passed = sum(1 for r in RESULTS if r["outcome"] == "passed")
    failed = sum(1 for r in RESULTS if r["outcome"] == "failed")
    print(f"\n结果已写入 {path}：通过 {passed}，失败 {failed}")
