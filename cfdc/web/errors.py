"""Small, explicitly public HTTP errors; exception internals stay server-side."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PublicError(BaseModel):
    code: str
    message: str
    fields: dict[str, str] = Field(default_factory=dict)
    latest_revision: int | None = None
    session_id: str | None = None
    receipt_saved: bool = False


class ErrorResponse(BaseModel):
    error: PublicError


class APIError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        **details,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.public = PublicError(code=code, message=message, **details)
