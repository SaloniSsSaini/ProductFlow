"""Health check response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Standard health probe payload for load balancers and orchestrators."""

    status: Literal["ok", "degraded"] = Field(
        description="Overall service health based on dependency checks.",
    )
    service: str = Field(description="Application name.")
    environment: str = Field(description="Deployment environment.")
    database: Literal["connected", "disconnected"] = Field(
        description="PostgreSQL connectivity status.",
    )
    timestamp: datetime = Field(description="UTC time when the check was performed.")
