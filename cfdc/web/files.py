"""Controlled upload storage; browser file identifiers never encode local paths."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from cfdc.web.errors import APIError
from cfdc.web.schemas import UploadResponse

MAX_UPLOAD_BYTES = 128 * 1024 * 1024


class FileStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def save(
        self, upload: UploadFile, *, session_id: str | None
    ) -> UploadResponse:
        name = Path((upload.filename or "").replace("\\", "/")).name
        suffix = Path(name).suffix.lower()
        if suffix not in {".csv", ".json", ".zip"}:
            raise APIError("unsupported_file", "请选择 CSV、JSON 或 ZIP 文件。", 422)
        if len(name.encode("utf-8")) > 240:
            raise APIError("filename_too_long", "文件名过长，请缩短后再上传。", 422)
        file_id = str(uuid4())
        directory = self.root / file_id
        directory.mkdir(mode=0o700)
        path = directory / f"source{suffix}"
        size = 0
        try:
            with path.open("xb") as stream:
                while chunk := await upload.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise APIError(
                            "file_too_large", "文件超过 128 MiB 上传上限。", 413
                        )
                    stream.write(chunk)
            (directory / "metadata.json").write_text(
                json.dumps(
                    {
                        "filename": name,
                        "suffix": suffix,
                        "session_id": session_id,
                        "size": size,
                    }
                ),
                encoding="utf-8",
            )
        except Exception:
            path.unlink(missing_ok=True)
            (directory / "metadata.json").unlink(missing_ok=True)
            directory.rmdir()
            raise
        finally:
            await upload.close()
        return UploadResponse(file_id=file_id, filename=name, size=size)

    def resolve(self, file_id: str, *, session_id: str | None) -> Path:
        try:
            identifier = str(UUID(file_id))
            directory = (self.root / identifier).resolve()
            if directory.parent != self.root:
                raise ValueError("outside upload store")
            metadata = json.loads(
                (directory / "metadata.json").read_text(encoding="utf-8")
            )
            if metadata.get("session_id") != session_id:
                raise APIError(
                    "file_task_mismatch",
                    "此文件不属于当前任务，请在当前任务重新上传。",
                    409,
                )
            suffix = metadata["suffix"]
            if suffix not in {".csv", ".json", ".zip"}:
                raise ValueError("unsupported stored file")
            path = (directory / f"source{suffix}").resolve()
            if path.parent != directory or not path.is_file():
                raise ValueError("upload unavailable")
            return path
        except (OSError, ValueError, KeyError, TypeError):
            raise APIError(
                "file_not_found", "上传文件已不可用，请重新上传。", 404
            ) from None
