"""Non-destructive environment checks shared by the CLI and WebUI.

The doctor deliberately reports capabilities and actionable outcomes rather
than dumping environment variables.  In particular, credentials never enter
the returned structure and a configured non-loopback Ollama endpoint is only
reported as unprobed.

The writable-directory check creates and immediately removes one bounded probe
file.  It does not modify project sources or retain environment data.
"""

from __future__ import annotations

import os
import platform
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class DoctorStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class DoctorCheck:
    check_id: str
    status: DoctorStatus
    message_cn: str
    required: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.check_id,
            "status": self.status.value,
            "message_cn": self.message_cn,
            "required": self.required,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]
    generated_at: str
    doctor_version: str = "cfdc-doctor/v1"

    @property
    def required_failures(self) -> tuple[DoctorCheck, ...]:
        return tuple(
            item
            for item in self.checks
            if item.required and item.status == DoctorStatus.FAIL
        )

    @property
    def status(self) -> DoctorStatus:
        if self.required_failures:
            return DoctorStatus.FAIL
        if any(item.status == DoctorStatus.WARN for item in self.checks):
            return DoctorStatus.WARN
        return DoctorStatus.PASS

    @property
    def ok(self) -> bool:
        return not self.required_failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "doctor_version": self.doctor_version,
            "generated_at": self.generated_at,
            "status": self.status.value,
            "ok": self.ok,
            "required_failures": [item.check_id for item in self.required_failures],
            "checks": [item.to_dict() for item in self.checks],
        }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _python_check() -> DoctorCheck:
    version = tuple(sys.version_info[:3])
    if version < (3, 11, 0):
        return DoctorCheck(
            "python",
            DoctorStatus.FAIL,
            "Python 版本过低，需要 Python 3.11 或更高版本。",
            required=True,
            details={"version": platform.python_version(), "minimum": "3.11"},
        )
    return DoctorCheck(
        "python",
        DoctorStatus.PASS,
        "Python 版本满足要求。",
        required=True,
        details={
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
    )


def _resource_check() -> DoctorCheck:
    required_files = (
        "resources/physical_training_cases.v1.json",
        "resources/audit_cases.v1.json",
        "resources/control_route_registry.v2.7.1.json",
    )
    missing: list[str] = []
    try:
        root = files("cfdc.kernel")
        for relative in required_files:
            candidate = root.joinpath(*relative.split("/"))
            if not candidate.is_file():
                missing.append(relative)
    except (AttributeError, ImportError, OSError, TypeError):
        missing = list(required_files)
    if missing:
        return DoctorCheck(
            "resources",
            DoctorStatus.FAIL,
            "Kernel 资源目录不完整。",
            required=True,
            details={"missing": missing},
        )
    return DoctorCheck(
        "resources",
        DoctorStatus.PASS,
        "Kernel 资源目录可读取。",
        required=True,
        details={"checked": list(required_files)},
    )


def _session_dir_check(session_dir: Path) -> DoctorCheck:
    root = Path(session_dir)
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=root, prefix=".doctor-", delete=False
        ) as handle:
            handle.write("ok\n")
            probe = Path(handle.name)
        probe.unlink(missing_ok=True)
    except (OSError, ValueError) as exc:
        return DoctorCheck(
            "session_dir",
            DoctorStatus.FAIL,
            "会话目录不可写。",
            required=True,
            details={"error": type(exc).__name__},
        )
    return DoctorCheck(
        "session_dir",
        DoctorStatus.PASS,
        "会话目录可创建且可写。",
        required=True,
        details={"configured": True},
    )


def _registry_check() -> DoctorCheck:
    try:
        from cfdc.kernel.cases import public_case_catalog

        catalog = public_case_catalog()
        kinds = {str(item.get("kind")) for item in catalog.values()}
        if not catalog or not {"training", "audit"} <= kinds:
            raise ValueError("case_registry_incomplete")
    except (
        AttributeError,
        ImportError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        return DoctorCheck(
            "case_registry",
            DoctorStatus.FAIL,
            "注册案例目录加载失败。",
            required=True,
            details={"error": type(exc).__name__},
        )
    return DoctorCheck(
        "case_registry",
        DoctorStatus.PASS,
        "注册案例目录已加载。",
        required=True,
        details={"case_count": len(catalog), "kinds": sorted(kinds)},
    )


def _rag_check(rag_index_dir: Path | None) -> DoctorCheck:
    if rag_index_dir is None or not str(rag_index_dir).strip():
        return DoctorCheck(
            "rag",
            DoctorStatus.WARN,
            "未配置本地 RAG；这不影响无 RAG 的 Kernel 流程。",
            details={"configured": False, "initialized": False},
        )
    root = Path(rag_index_dir)
    if not root.is_dir() or not (root / "CURRENT").is_file():
        return DoctorCheck(
            "rag",
            DoctorStatus.WARN,
            "RAG 目录未初始化；请先建立本地索引，或关闭 RAG。",
            details={"configured": True, "initialized": False},
        )
    try:
        from cfdc.rag import load_index

        index = load_index(root, load_encoder=False)
        snapshot = str(index.index_snapshot)
    except (ImportError, KeyError, OSError, TypeError, ValueError) as exc:
        return DoctorCheck(
            "rag",
            DoctorStatus.WARN,
            "RAG 索引存在但校验失败；请重建索引或关闭 RAG。",
            details={
                "configured": True,
                "initialized": False,
                "error": type(exc).__name__,
            },
        )
    return DoctorCheck(
        "rag",
        DoctorStatus.PASS,
        "本地 RAG 索引已初始化。",
        details={"configured": True, "initialized": True, "snapshot": snapshot},
    )


def _loopback(host: str | None) -> bool:
    return str(host or "").casefold().strip("[]") in {
        "127.0.0.1",
        "localhost",
        "::1",
    }


def _ollama_check(
    base_url: str | None,
    model: str | None,
    *,
    probe: bool,
) -> DoctorCheck:
    raw_url = str(base_url or os.getenv("CFDC_LLM_BASE_URL") or "").strip()
    model_name = str(model or os.getenv("CFDC_LLM_MODEL") or "").strip()
    if not raw_url or not model_name:
        return DoctorCheck(
            "ollama",
            DoctorStatus.WARN,
            "本地 Ollama 未配置；需要真实模型时请填写 Base URL 和 Model。",
            details={
                "configured": False,
                "probed": False,
                "model_configured": bool(model_name),
            },
        )
    parsed = urlparse(raw_url)
    if not _loopback(parsed.hostname):
        return DoctorCheck(
            "ollama",
            DoctorStatus.WARN,
            "已配置远程模型地址；doctor 不会主动访问非本机服务。",
            details={
                "configured": True,
                "probed": False,
                "host_kind": "remote",
                "model_configured": True,
            },
        )
    if not probe:
        return DoctorCheck(
            "ollama",
            DoctorStatus.WARN,
            "已配置本地 Ollama，但本次未执行网络探测。",
            details={
                "configured": True,
                "probed": False,
                "host_kind": "loopback",
                "model_configured": True,
            },
        )
    origin = f"{parsed.scheme or 'http'}://{parsed.netloc}"
    request = Request(f"{origin}/api/tags", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=2.0) as response:
            payload = response.read()
        import json

        value = json.loads(payload.decode("utf-8"))
        names = {
            str(item.get("name") or item.get("model") or "")
            for item in value.get("models", ())
            if isinstance(item, dict)
        }
        if model_name not in names:
            return DoctorCheck(
                "ollama",
                DoctorStatus.WARN,
                "Ollama 服务可访问，但指定模型未安装。",
                details={
                    "configured": True,
                    "probed": True,
                    "host_kind": "loopback",
                    "model_available": False,
                },
            )
    except (OSError, TypeError, UnicodeError, ValueError) as exc:
        return DoctorCheck(
            "ollama",
            DoctorStatus.WARN,
            "无法访问本地 Ollama；可启动服务后重试。",
            details={
                "configured": True,
                "probed": True,
                "host_kind": "loopback",
                "error": type(exc).__name__,
            },
        )
    return DoctorCheck(
        "ollama",
        DoctorStatus.PASS,
        "本地 Ollama 服务和指定模型可用。",
        details={
            "configured": True,
            "probed": True,
            "host_kind": "loopback",
            "model_available": True,
        },
    )


def run_doctor(
    *,
    session_dir: str | Path | None = None,
    rag_index_dir: str | Path | None = None,
    ollama_base_url: str | None = None,
    ollama_model: str | None = None,
    api_key: str | None = None,
    probe_ollama: bool = True,
) -> DoctorReport:
    """Run safe local checks and return a JSON-serializable report.

    ``api_key`` is accepted to make callers explicit about the credential
    boundary, but it is intentionally unused and never copied into a report.
    """

    del api_key
    configured_session_dir = Path(
        session_dir
        or os.getenv("CFDC_KERNEL_SESSION_DIR")
        or Path("output") / "kernel-sessions"
    )
    configured_rag = (
        Path(rag_index_dir)
        if rag_index_dir is not None and str(rag_index_dir).strip()
        else None
    )
    checks = (
        _python_check(),
        _resource_check(),
        _session_dir_check(configured_session_dir),
        _registry_check(),
        _rag_check(configured_rag),
        _ollama_check(ollama_base_url, ollama_model, probe=probe_ollama),
    )
    return DoctorReport(checks=checks, generated_at=_utc_now())


__all__ = ["DoctorCheck", "DoctorReport", "DoctorStatus", "run_doctor"]
