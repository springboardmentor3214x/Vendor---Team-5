"""Minimal auth smoke tests for the current FastAPI backend.

Scope note:
- These tests only exercise real routes that currently exist in the backend.
- The route-layer role enforcement helper `require_roles(...)` exists in
  `backend/app/api/auth.py`, but it is not currently applied to any live route.
- Therefore, this test file documents that admin-only / role-restricted behavior
  is not yet implemented in the route layer and should not be assumed.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.main import app

client = TestClient(app)

ADMIN_EMAIL = "pranjali.admin2@example.com"
ADMIN_PASSWORD = "Password123"
VENDOR_EMAIL = "vendor.user1@example.com"
VENDOR_PASSWORD = "Password123"


@pytest.fixture(scope="module")
def auth_tokens() -> dict[str, str]:
    """Create or reuse a minimal auth flow for current backend behavior only."""
    register_payload = {
        "fullName": "Admin User Test",
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "confirmPassword": ADMIN_PASSWORD,
        "role": "Administrator",
    }

    register_response = client.post("/auth/register", json=register_payload)
    if register_response.status_code not in (200, 201, 400):
        pytest.fail(f"Unexpected register response: {register_response.status_code}")

    if register_response.status_code == 400:
        duplicate_detail = register_response.json().get("detail", "")
        assert duplicate_detail in {"Email already registered", "Email already registered"}

    login_response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert me_response.status_code == 200, me_response.text
    me_data = me_response.json()
    assert me_data["email"] == ADMIN_EMAIL

    return {"access_token": login_data["access_token"]}


def test_register_handles_duplicate_user_cleanly() -> None:
    """Register either succeeds once or returns a clean duplicate-user error."""
    payload = {
        "fullName": "Admin User Test",
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "confirmPassword": ADMIN_PASSWORD,
        "role": "Administrator",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code in (200, 201, 400), response.text

    if response.status_code == 400:
        assert response.json()["detail"] == "Email already registered"


def test_login_returns_access_token() -> None:
    response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_invalid_stored_hash_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """A malformed legacy password hash must not turn an invalid login into a 500."""
    email = "invalid-hash-login@example.com"
    payload = {
        "fullName": "Invalid Hash Login Test",
        "email": email,
        "password": ADMIN_PASSWORD,
        "confirmPassword": ADMIN_PASSWORD,
        "role": "Administrator",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code in (200, 201, 400), response.text

    def invalid_hash(*_: object) -> bool:
        raise ValueError("hash could not be identified")

    monkeypatch.setattr(auth_api, "verify_password", invalid_hash)
    response = client.post("/auth/login", json={"email": email, "password": ADMIN_PASSWORD})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_returns_current_user_for_bearer_token(auth_tokens: dict[str, str]) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == ADMIN_EMAIL
    assert data["role"] == "Administrator"


def test_current_routes_are_auth_protected_only_not_role_restricted() -> None:
    """Document current implementation reality:

    The only authentication enforcement currently present on live routes is
    `Depends(get_current_user)` on `/auth/me` and related auth routes.

    The helper `require_roles(...)` exists in `backend/app/api/auth.py`, but it is
    not applied to any live route. Therefore, this test asserts the current
    protected route behavior only, not a role-based 403 contract.
    """
    response = client.get("/auth/me")
    assert response.status_code == 401, response.text
    assert "detail" in response.json()
    assert response.json()["detail"] in ["Not authenticated", "Could not validate credentials"]
