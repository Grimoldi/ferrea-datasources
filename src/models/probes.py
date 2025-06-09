from __future__ import annotations

from enum import StrEnum, auto

from pydantic import BaseModel, Field


class HealthProbe(BaseModel):
    status: HealthStatus
    entities: list[Entity]


class Entity(BaseModel):
    name: str
    status: HealthStatus
    internal_status: bool = Field(exclude=True)

    def get_status(self) -> bool:
        return self.internal_status


class HealthStatus(StrEnum):
    HEALTHY = auto()
    UNHEALTHY = auto()
