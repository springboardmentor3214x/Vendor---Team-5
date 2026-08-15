from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.auth import require_frontend_route_access


def request(path: str, method: str = "GET") -> Request:
    return Request({"type": "http", "method": method, "path": path, "headers": []})


def test_frontend_role_policy_allows_the_matching_module_role() -> None:
    user = SimpleNamespace(role="Finance Officer")
    assert require_frontend_route_access(request("/procurement/invoices"), user) is user


def test_frontend_role_policy_blocks_unrelated_module_access() -> None:
    with pytest.raises(HTTPException, match="access this module") as error:
        require_frontend_route_access(request("/procurement/procurement-requests"), SimpleNamespace(role="Finance Officer"))
    assert error.value.status_code == 403


def test_read_only_roles_cannot_modify_managed_modules() -> None:
    with pytest.raises(HTTPException, match="modify this module") as error:
        require_frontend_route_access(request("/performance/quality", "POST"), SimpleNamespace(role="Auditor"))
    assert error.value.status_code == 403
