from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class WaterRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    time_on: datetime
    time_off: datetime | None
    level: str  # "low" | "medium" | "high"


class ElectricityRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    time_on: datetime
    time_off: datetime | None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    size: int
    total: int


class WaterStatusResponse(BaseModel):
    status: int = Field(ge=0, le=3)


class ElectricityStatusResponse(BaseModel):
    status: bool
