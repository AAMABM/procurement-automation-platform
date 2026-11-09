"""Role / Permission schemas."""
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel


class PermissionResponse(ORMModel):
    id: UUID
    code: str
    description: str


class RoleResponse(ORMModel):
    id: UUID
    name: str
    description: str
    is_system_role: bool
    permissions: list[PermissionResponse] = Field(default_factory=list)