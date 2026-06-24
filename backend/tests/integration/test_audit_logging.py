"""Tests for structured audit logging of key actions."""

from __future__ import annotations

import json
import logging

import pytest
from fastapi.testclient import TestClient


def _audit_payloads(caplog: pytest.LogCaptureFixture) -> list[dict]:
    return [
        json.loads(record.message) for record in caplog.records if record.name == "careerflow.audit"
    ]


def test_login_emits_structured_audit_record(
    client: TestClient, registered_user: dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="careerflow.audit"):
        client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
    logins = [p for p in _audit_payloads(caplog) if p["action"] == "login"]
    assert logins, "expected a login audit record"
    record = logins[-1]
    assert record["status"] == "success"
    assert record["user_id"]
    assert record["timestamp"]


def test_failed_login_is_audited(
    client: TestClient, registered_user: dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="careerflow.audit"):
        client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "wrong-password"},
        )
    logins = [p for p in _audit_payloads(caplog) if p["action"] == "login"]
    assert any(p["status"] == "failure" for p in logins)


def test_offer_decision_is_audited(
    client: TestClient, auth_headers: dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    app_id = client.post(
        "/api/v1/applications", json={"role_title": "Engineer"}, headers=auth_headers
    ).json()["id"]
    with caplog.at_level(logging.INFO, logger="careerflow.audit"):
        client.post(
            f"/api/v1/applications/{app_id}/offers",
            json={"base_salary": 100000, "decision": "negotiating"},
            headers=auth_headers,
        )
    offers = [p for p in _audit_payloads(caplog) if p["action"] == "offer_decision"]
    assert offers
    assert offers[-1]["decision"] == "negotiating"
