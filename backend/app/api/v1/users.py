"""
User administration endpoints.

Authorization:
    All routes require the appropriate `users:*` permission (RBAC).
    `/users/me` is available to any authenticated user.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, UserSvc, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current authenticated user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get(
    "",
    response_model=Page[UserResponse],
    dependencies=[Depends(require_permissions(PermissionCode.USERS_READ.value))],
)
async def list_users(
    users: UserSvc,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> Page[UserResponse]:
    items, total = await users.list(page=page, page_size=page_size)
    return Page[UserResponse](
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PermissionCode.USERS_WRITE.value))],
)
async def create_user(payload: UserCreate, users: UserSvc) -> UserResponse:
    created = await users.create(payload)
    return UserResponse.model_validate(created)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions(PermissionCode.USERS_READ.value))],
)
async def get_user(user_id: UUID, users: UserSvc) -> UserResponse:
    user = await users.get(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions(PermissionCode.USERS_WRITE.value))],
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    users: UserSvc,
    current_user: CurrentUser,
) -> UserResponse:
    updated = await users.update(user_id, payload, acting_user=current_user)
    return UserResponse.model_validate(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissions(PermissionCode.USERS_DELETE.value))],
)
async def delete_user(user_id: UUID, users: UserSvc, current_user: CurrentUser) -> None:
    await users.delete(user_id, acting_user=current_user)