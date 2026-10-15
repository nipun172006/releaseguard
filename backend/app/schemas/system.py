from typing import Literal

from pydantic import BaseModel


class RootResponse(BaseModel):
    service: str
    message: str
    documentation: str


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    checks: dict[str, str]
