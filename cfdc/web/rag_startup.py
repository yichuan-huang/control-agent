"""Prepare the packaged advisory RAG index in the WebUI's background worker."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from cfdc.rag import (
    RAG_SCHEMA_VERSION,
    RETRIEVAL_POLICY_VERSION,
    build_index,
    load_index,
    load_knowledge_pack,
    retrieval_policy_fingerprint,
    retrieval_policy_settings,
)

_WARMUP_QUERY = "control-system knowledge readiness"


class BuiltinRAGStartupError(RuntimeError):
    """A classified startup failure with a bounded public recovery message."""

    def __init__(self, message: str, *, reason: str = "unknown") -> None:
        super().__init__(message)
        self.reason = reason

    @property
    def public_message(self) -> str:
        messages = {
            "dependencies": "内置知识库依赖缺失；请执行 uv sync --locked 恢复依赖后重新启动。",
            "permissions": "内置知识库索引目录不可写；请检查索引目录权限后重新启动。",
            "model": "内置知识库编码模型无法加载；请检查网络或本地 Hugging Face 缓存后重新启动。",
            "index": "内置知识库索引构建失败；请检查模型缓存和索引目录，环境自检可帮助定位。",
            "package": "内置知识包校验失败；请恢复当前版本的知识包文件后重新启动。",
            "unknown": "内置知识库准备失败；请检查依赖、网络、模型缓存和索引目录，环境自检可帮助定位。",
        }
        return messages.get(self.reason, messages["unknown"])


@dataclass(frozen=True)
class PreparedRAGIndex:
    """Server-owned immutable RAG snapshot used by every WebUI task."""

    index_dir: Path
    snapshot: str


def _managed_index_dir(index_dir: str | Path | None) -> Path:
    if index_dir is not None and str(index_dir).strip():
        return Path(index_dir)
    configured = str(os.getenv("CFDC_RAG_INDEX_DIR") or "").strip()
    return Path(configured) if configured else Path("output") / "rag-index"


def _expected_datasets(pack: Any) -> list[dict[str, str]]:
    metadata = pack.evaluation_metadata
    return [
        {"dataset": str(metadata["dataset"]), "sha256": str(metadata["sha256"])},
        *[
            {
                "dataset": str(item["dataset"]),
                "sha256": str(item["sha256"]),
            }
            for item in metadata.get("additional_datasets", [])
        ],
    ]


def _is_current_builtin_snapshot(manifest: dict[str, Any], pack: Any) -> bool:
    pack_manifest = manifest.get("knowledge_pack")
    policy = manifest.get("retrieval_policy")
    source_files = manifest.get("source_files")
    if not isinstance(pack_manifest, dict) or not isinstance(policy, dict):
        return False
    if not isinstance(source_files, list) or not source_files:
        return False
    if manifest.get("schema_version") != RAG_SCHEMA_VERSION:
        return False
    if manifest.get("retrieval_policy_version") != RETRIEVAL_POLICY_VERSION:
        return False
    if manifest.get("embedding_model") != pack.evaluation_metadata["embedding_model"]:
        return False
    if (
        manifest.get("embedding_model_revision")
        != pack.evaluation_metadata["embedding_revision"]
    ):
        return False
    expected_policy = retrieval_policy_settings(
        float(pack.evaluation_metadata["relevance_threshold"]),
        "bundled-pack-dev",
    )
    if policy != expected_policy:
        return False
    if manifest.get("retrieval_policy_fingerprint") != (
        retrieval_policy_fingerprint(expected_policy)
    ):
        return False
    if pack_manifest.get("pack_id") != pack.pack_id:
        return False
    if pack_manifest.get("version") != pack.version:
        return False
    if pack_manifest.get("authority") != pack.authority:
        return False
    if pack_manifest.get("excluded_artifact_ids") != list(pack.excluded_artifact_ids):
        return False
    evaluation = pack_manifest.get("evaluation")
    if not isinstance(evaluation, dict):
        return False
    if evaluation.get("datasets") != _expected_datasets(pack):
        return False
    if evaluation.get("cases") != len(pack.evaluation["cases"]):
        return False
    return {item.get("kind") for item in source_files if isinstance(item, dict)} == {
        "builtin_registry",
        "curated_pack",
    }


def _safe_startup_error(exc: Exception, *, phase: str) -> BuiltinRAGStartupError:
    if isinstance(exc, ImportError) or isinstance(exc.__cause__, ImportError):
        return BuiltinRAGStartupError(
            "内置 RAG 依赖未安装；请执行 uv sync --locked。", reason="dependencies"
        )
    if isinstance(exc, PermissionError):
        return BuiltinRAGStartupError(
            "内置 RAG 索引目录不可写；请检查 output/rag-index 的目录权限。",
            reason="permissions",
        )
    if phase == "warmup":
        return BuiltinRAGStartupError(
            "内置 RAG 编码模型无法加载；请检查网络或本地 Hugging Face 缓存。",
            reason="model",
        )
    return BuiltinRAGStartupError(
        "内置 RAG 索引构建失败；请检查依赖、模型缓存和索引目录。", reason="index"
    )


def _warm_encoder(index: Any) -> None:
    if index.encoder is None:
        raise RuntimeError("RAG encoder was not loaded")
    vector = np.asarray(index.encoder.encode([_WARMUP_QUERY], is_query=True))
    if vector.shape != (1, int(index.manifest["embedding_dimension"])):
        raise ValueError("RAG encoder warmup dimension mismatch")
    if not np.isfinite(vector).all():
        raise ValueError("RAG encoder warmup returned non-finite values")


def prepare_builtin_rag_index(
    index_dir: str | Path | None = None,
    *,
    encoder: Any | None = None,
) -> PreparedRAGIndex:
    """Build or reuse the exact packaged index, then load and warm its encoder."""

    root = _managed_index_dir(index_dir)
    try:
        pack = load_knowledge_pack()
    except Exception as exc:
        raise BuiltinRAGStartupError(
            "内置 RAG 知识包校验失败；请重新安装当前版本后重试。", reason="package"
        ) from exc
    existing = None
    try:
        existing = load_index(root, load_encoder=False)
    except (FileNotFoundError, KeyError, OSError, TypeError, ValueError):
        pass

    if existing is None or not _is_current_builtin_snapshot(existing.manifest, pack):
        try:
            built = build_index(
                None,
                root,
                encoder=encoder,
                include_builtin=True,
                include_curated=True,
            )
        except Exception as exc:
            raise _safe_startup_error(exc, phase="build") from exc
        snapshot = built.index_snapshot
    else:
        snapshot = existing.index_snapshot

    try:
        warmed = load_index(
            root,
            snapshot_name=snapshot,
            encoder=encoder,
            load_encoder=True,
        )
        _warm_encoder(warmed)
    except Exception as exc:
        raise _safe_startup_error(exc, phase="warmup") from exc
    return PreparedRAGIndex(index_dir=root, snapshot=snapshot)


__all__ = [
    "BuiltinRAGStartupError",
    "PreparedRAGIndex",
    "prepare_builtin_rag_index",
]
