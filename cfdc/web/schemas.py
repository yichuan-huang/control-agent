"""Versioned HTTP input models, separate from immutable Kernel artifacts."""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Credentials(InputModel):
    base_url: str = Field(default="", max_length=2048)
    model: str = Field(default="", max_length=256)
    api_key: str = Field(default="", max_length=8192, repr=False)

    @field_validator("base_url")
    @classmethod
    def address(cls, value: str) -> str:
        value = value.strip()
        if value:
            parsed = urlsplit(value)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("模型地址必须是 HTTP(S) 地址，凭据请填写在密钥栏。")
        return value


class DraftRequest(InputModel):
    draft: dict[str, Any]
    case_id: str = Field(default="", max_length=128)


class CreateRequest(InputModel):
    request_id: UUID
    draft: dict[str, Any] | None = None
    task: dict[str, Any] | None = None
    case_id: str = Field(default="", max_length=128)
    evidence_mode: Literal["automatic", "exercise_bundle"] = "automatic"
    confirmed: bool = False
    use_rag: bool = True
    credentials: Credentials = Field(default_factory=Credentials, repr=False)

    @model_validator(mode="after")
    def one_source(self):
        if (self.draft is None) == (self.task is None):
            raise ValueError("请提供表单草稿或完整任务合同中的一种。")
        return self


class ActionInput(InputModel):
    text: str = Field(default="", max_length=1024 * 1024)
    mode: Literal["natural_language", "json"] = "natural_language"
    confirmed: bool = False
    payload: dict[str, Any] | None = None
    file_ids: list[UUID] = Field(default_factory=list, max_length=100)
    stopped_on_limit: bool = False


class ActionRequest(InputModel):
    request_id: UUID
    expected_revision: int = Field(ge=0, strict=True)
    action: str = Field(min_length=1, max_length=80)
    input: ActionInput = Field(default_factory=ActionInput)
    credentials: Credentials = Field(default_factory=Credentials, repr=False)


class ImportRequest(InputModel):
    request_id: UUID
    file_id: UUID


class ProbeRequest(InputModel):
    credentials: Credentials = Field(default_factory=Credentials, repr=False)


class DoctorRequest(ProbeRequest):
    use_rag: bool = True


class ArtifactValidationRequest(InputModel):
    payload: dict[str, Any]


class DraftResponse(BaseModel):
    draft: dict[str, Any]


class DraftValidationResponse(BaseModel):
    task: dict[str, Any]
    summary: str


class ArtifactValidationResponse(BaseModel):
    valid: bool = True
    artifact: dict[str, Any]


class RAGStatus(BaseModel):
    status: Literal["preparing", "ready", "error"]
    message: str
    snapshot: str | None = None


class ConfigResponse(BaseModel):
    base_url: str
    model: str
    rag: RAGStatus
    version: str = "0.3.4"


class ProbeResponse(BaseModel):
    connected: bool
    message: str


class DoctorCheck(BaseModel):
    name: str
    status: str
    message: str


class DoctorResponse(BaseModel):
    checks: list[DoctorCheck]


class CaseCard(BaseModel):
    id: str
    title: str
    category: Literal["engineering", "audit"]
    description: str
    data_source: str
    scope: str


class CaseList(BaseModel):
    items: list[CaseCard]


class CaseDetail(CaseCard):
    draft: dict[str, Any]
    task: dict[str, Any]
    learning: dict[str, Any]


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
