"""
Shared schema primitives.

Why this exists:
    Reusable envelope for pagination + timestamp conventions. Frontends
    consume a consistent envelope, avoiding per-endpoint guesswork.
"""
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for schemas that hydrate from ORM objects."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=200)


class IdResponse(BaseModel):
    id: UUID