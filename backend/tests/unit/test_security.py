"""Unit tests: hashing + JWT round-trip + type enforcement."""
import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    h = hash_password("hunter2-testing")
    assert h != "hunter2-testing"
    assert verify_password("hunter2-testing", h)
    assert not verify_password("wrong", h)


def test_argon2_different_salt_each_time():
    assert hash_password("same") != hash_password("same")


def test_access_token_roundtrip():
    tok = create_access_token("user-123")
    payload = decode_token(tok, expected_type="access")
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_rejects_access_type():
    tok = create_access_token("user-123")
    with pytest.raises(AuthenticationError):
        decode_token(tok, expected_type="refresh")


def test_invalid_token_raises():
    with pytest.raises(AuthenticationError):
        decode_token("not.a.jwt", expected_type="access")