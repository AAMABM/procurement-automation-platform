"""
Idempotent database bootstrap.

Why this exists:
    New deployments need system roles + permission catalog seeded before
    the first user logs in. Running this on every boot makes containers
    self-healing and removes the "did someone run the seed script?" failure mode.

Enterprise decisions:
    - Idempotent (uses upsert-style checks) — safe to run on every deploy.
    - No hardcoded credentials beyond `FIRST_SUPERUSER_*` (env-only, prod-disabled).
    - Seeds *roles* and *permissions* but not mock users/data.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.permissions import SYSTEM_ROLES, PermissionCode
from app.core.security import hash_password
from app.models.role import Permission, Role
from app.models.user import User

logger = get_logger(__name__)


async def seed_permissions_and_roles(session: AsyncSession) -> None:
    # --- Permissions ---
    existing_perms = {
        p.code for p in (await session.execute(select(Permission))).scalars().all()
    }
    for code in PermissionCode:
        if code.value not in existing_perms:
            session.add(Permission(code=code.value, description=code.name))
    await session.flush()

    # --- Roles ---
    existing_roles = {
        r.name: r for r in (await session.execute(select(Role))).scalars().all()
    }
    all_perms = {
        p.code: p
        for p in (await session.execute(select(Permission))).scalars().all()
    }
    for role_name, config in SYSTEM_ROLES.items():
        role = existing_roles.get(role_name)
        if role is None:
            role = Role(
                name=role_name,
                description=config["description"],
                is_system_role=True,
            )
            session.add(role)
        # Reconcile permissions (additive — never remove custom grants)
        for code in config["permissions"]:
            perm = all_perms.get(code)
            if perm and perm not in role.permissions:
                role.permissions.append(perm)
    await session.commit()


async def seed_first_superuser(session: AsyncSession) -> None:
    settings = get_settings()
    if not settings.FIRST_SUPERUSER_EMAIL or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info("superuser_seed_skipped", reason="env_not_set")
        return
    if settings.APP_ENV == "production":
        logger.warning("superuser_seed_skipped", reason="production_env")
        return

    existing = await session.scalar(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL.lower())
    )
    if existing:
        logger.info("superuser_seed_skipped", reason="already_exists")
        return

    admin_role = await session.scalar(select(Role).where(Role.name == "admin"))
    user = User(
        email=settings.FIRST_SUPERUSER_EMAIL.lower(),
        hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
        full_name="Platform Administrator",
        is_active=True,
        is_superuser=True,
    )
    if admin_role:
        user.roles.append(admin_role)
    session.add(user)
    await session.commit()
    logger.info("superuser_created", email=user.email)


async def init_db(session: AsyncSession) -> None:
    await seed_permissions_and_roles(session)
    await seed_first_superuser(session)