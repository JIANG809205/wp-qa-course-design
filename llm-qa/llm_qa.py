"""大模型测试助手：多后端（DeepSeek 云端 / Ollama 本地 / mock）。

四个任务对应课程设计要求的四个环节：
  1. cases   —— 需求 → 测试用例（JSON）
  2. scripts —— 用例 → Selenium 脚本
  3. triage  —— 失败日志 → 归因（环境/脚本/缺陷）
  4. report  —— 性能数据 → 分析段落
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------- 配置

DEFAULT_BASE_URLS = {
    # 阿里云百炼 OpenAI 兼容端点（本机实测可用，同时托管 Qwen 与 DeepSeek）
    "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "deepseek": "https://api.deepseek.com",
    "ollama": "http://localhost:11434",
    "mock": "",
}

DEFAULT_MODELS = {
    "dashscope": "deepseek-v4.1-flash",
    "deepseek": "deepseek-chat",
    "ollama": "qwen2.5:3b",
    "mock": "mock-1",
}


@dataclass
class Settings:
    provider: str = "mock"
    model: str = ""
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.2
    max_tokens: int = 8000

    def resolve(self) -> "Settings":
        self.model = self.model or DEFAULT_MODELS.get(self.provider, "")
        self.base_url = self.base_url or DEFAULT_BASE_URLS.get(self.provider, "")
        if self.provider == "dashscope":
            self.api_key = self.api_key or os.getenv("DASHSCOPE_API_KEY", "") or os.getenv("DEEPSEEK_API_KEY", "")
        if self.provider == "deepseek":
            self.api_key = self.api_key or os.getenv("DEEPSEEK_API_KEY", "")
        return self


# ---------------------------------------------------------------- 后端

class Backend:
    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError


class OpenAICompatBackend(Backend):
    """DeepSeek 与 Ollama 都提供 OpenAI 兼容接口"""

    def __init__(self, settings: Settings):
        from openai import OpenAI

        self.settings = settings
        base = settings.base_url.rstrip("/")
        if not base.endswith("/v1"):
            base += "/v1"
        self.client = OpenAI(
            api_key=settings.api_key or "ollama",
            base_url=base,
            timeout=180,
        )

    def complete(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
        )
        msg = resp.choices[0].message
        content = (getattr(msg, "content", None) or "").strip()
        if not content:
            # 部分推理模型会把输出放在 reasoning_content，正文为空时兜底
            extra = getattr(msg, "model_extra", None) or {}
            content = (getattr(msg, "reasoning_content", None) or extra.get("reasoning_content") or "").strip()
        return content


class MockBackend(Backend):
    """离线占位：用于验证流水线（不产生真实质量数据）"""

    def complete(self, system: str, user: str) -> str:
        if "TASK:cases" in system:
            return json.dumps(
                [
                    {
                        "id": "TC-LLM-001",
                        "title": "登录页输入正确凭据可进入后台",
                        "precondition": "存在有效账号",
                        "steps": ["打开登录页", "输入账号密码", "点击登录"],
                        "expected": "跳转到后台仪表盘",
                        "method": "等价类划分",
                    },
                    {
                        "id": "TC-LLM-002",
                        "title": "登录页密码为空时被拦截",
                        "precondition": "无",
                        "steps": ["打开登录页", "只填账号", "点击登录"],
                        "expected": "提示必填，不进入后台",
                        "method": "边界值分析",
                    },
                ],
                ensure_ascii=False,
            )
        if "TASK:scripts" in system:
            return (
                "```java\n"
                "@Test\n"
                "public void loginSuccess() {\n"
                "    driver.get(BASE_URL + \"/wp-login.php\");\n"
                "    driver.findElement(By.id(\"user_login\")).sendKeys(\"admin\");\n"
                "    driver.findElement(By.id(\"user_pass\")).sendKeys(\"Admin@2026\");\n"
                "    driver.findElement(By.id(\"wp-submit\")).click();\n"
                "    Assert.assertTrue(driver.getCurrentUrl().contains(\"wp-admin\"));\n"
                "}\n```"
            )
        if "TASK:triage" in system:
            return json.dumps(
                {"category": "脚本问题", "reason": "元素定位在页面刷新后失效", "evidence_needed": "截图与 DOM 快照"},
                ensure_ascii=False,
            )
        return "（mock）性能数据表明首页在约 90 TPS 处饱和，瓶颈为单请求 PHP 渲染耗时。"


def build_backend(settings: Settings) -> Backend:
    if settings.provider == "mock":
        return MockBackend()
    if settings.provider in ("deepseek", "dashscope") and not settings.api_key:
        raise RuntimeError("缺少 API key（DASHSCOPE_API_KEY / DEEPSEEK_API_KEY），请写入 .env 或改用 --provider mock")
    return OpenAICompatBackend(settings)


# ---------------------------------------------------------------- 提示词

SYS_CASES = (
    "[TASK:cases] 你是一名资深软件测试工程师。请针对给定的功能点设计 8 到 10 条测试用例（不要超过 10 条），"
    "必须覆盖正向、负向、边界与异常场景，并写明所用的测试设计方法。"
    "只输出 JSON 数组，每个元素包含字段：id,title,precondition,steps(array),expected,method。"
    "不要输出解释文字，不要用 Markdown 代码块包裹。"
)

SYS_SCRIPTS = (
    "[TASK:scripts] 你是自动化测试工程师。请把给定用例改写成 Selenium 4 + TestNG 的 Java 测试方法。"
    "要求：使用显式等待、包含至少一个断言、方法名用英文、只输出 Java 代码，"
    "不要输出解释，不要用 Markdown 代码块包裹。"
)

SYS_TRIAGE = (
    "[TASK:triage] 你是缺陷分析师。给定一段失败的测试日志，判断失败原因属于以下哪一类："
    "环境问题、脚本问题、系统缺陷。只输出 JSON：{category, reason, evidence_needed}。"
    "不要在证据不足时臆断为系统缺陷。"
)

SYS_REPORT = (
    "[TASK:report] 你是性能测试分析师。根据给定的压测数据，写一段 150 字左右的中文分析，"
    "要点明：吞吐饱和点、响应时间劣化趋势、可能的瓶颈、下一步建议。"
)


def user_cases(feature: dict[str, Any]) -> str:
    return json.dumps(feature, ensure_ascii=False, indent=2)


def user_scripts(case: dict[str, Any]) -> str:
    return json.dumps(case, ensure_ascii=False, indent=2)


def user_triage(log: dict[str, Any]) -> str:
    return json.dumps(log, ensure_ascii=False, indent=2)


def user_report(perf: dict[str, Any]) -> str:
    return json.dumps(perf, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- 解析与度量

def strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json|java)?\s*(.*?)```", text, re.S)
    return m.group(1).strip() if m else text


def parse_json_array(text: str) -> list[dict] | None:
    raw = strip_fences(text)
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else None
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.S)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, list) else None
        except json.JSONDecodeError:
            return None


def java_syntax_ok(code: str) -> bool:
    """轻量校验：括号配对 + 关键结构存在（不做真编译）"""
    body = strip_fences(code)
    if body.count("{") != body.count("}"):
        return False
    has_assert = ("assert" in body.lower())
    has_driver = ("driver" in body)
    return has_assert and has_driver


@dataclass
class RunRecord:
    task: str
    provider: str
    model: str
    item_id: str
    raw: str
    ok: bool
    detail: dict[str, Any] = field(default_factory=dict)


def evaluate_cases(raw: str, reference_titles: list[str]) -> dict[str, Any]:
    cases = parse_json_array(raw)
    if cases is None:
        return {"valid_json": False, "count": 0, "fields_ok": 0, "overlap": 0}
    required = {"id", "title", "precondition", "steps", "expected", "method"}
    fields_ok = sum(1 for c in cases if required.issubset(c.keys()))
    overlap = 0
    for c in cases:
        title = str(c.get("title", ""))
        if any(_similar(title, ref) for ref in reference_titles):
            overlap += 1
    return {
        "valid_json": True,
        "count": len(cases),
        "fields_ok": fields_ok,
        "overlap": overlap,
    }


def _similar(a: str, b: str) -> bool:
    """粗粒度相似：字符二元组 Jaccard >= 0.35"""
    def grams(s: str) -> set[str]:
        s = re.sub(r"\s+", "", s)
        return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 2 else {s}

    ga, gb = grams(a), grams(b)
    if not ga or not gb:
        return False
    return len(ga & gb) / len(ga | gb) >= 0.35


def evaluate_triage(raw: str, gold: str) -> dict[str, Any]:
    text = strip_fences(raw)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        data = json.loads(m.group(0)) if m else {}
    cat = str(data.get("category", ""))
    return {"category": cat, "match": cat == gold, "has_reason": bool(data.get("reason"))}
