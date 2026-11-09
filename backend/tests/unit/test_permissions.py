"""Verify superuser wildcard + permission aggregation."""
from app.models.role import Permission, Role
from app.models.user import User


def test_superuser_has_wildcard():
    u = User(email="a@b.c", hashed_password="x", full_name="X", is_superuser=True)
    assert u.permission_codes == {"*"}


def test_role_permission_union():
    p1 = Permission(code="users:read")
    p2 = Permission(code="users:write")
    r1 = Role(name="r1"); r1.permissions = [p1]
    r2 = Role(name="r2"); r2.permissions = [p2]
    u = User(email="a@b.c", hashed_password="x", full_name="X")
    u.roles = [r1, r2]
    assert u.permission_codes == {"users:read", "users:write"}