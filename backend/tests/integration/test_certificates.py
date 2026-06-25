"""Integration tests for certificate endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_metadata_only(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/certificates",
        data={"name": "AWS SAA", "issuer": "Amazon", "issued_on": "2025-03-01"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "AWS SAA"
    assert body["has_file"] is False


def test_create_with_file_and_download(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/certificates",
        data={"name": "Scrum"},
        files={"file": ("cert.png", b"\x89PNG fake bytes", "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    cert = response.json()
    assert cert["has_file"] is True

    download = client.get(f"/api/v1/certificates/{cert['id']}/download", headers=auth_headers)
    assert download.status_code == 200
    assert download.content == b"\x89PNG fake bytes"


def test_update_and_delete(client: TestClient, auth_headers: dict[str, str]) -> None:
    cert_id = client.post(
        "/api/v1/certificates", data={"name": "Temp"}, headers=auth_headers
    ).json()["id"]

    patched = client.patch(
        f"/api/v1/certificates/{cert_id}",
        json={"issuer": "Coursera"},
        headers=auth_headers,
    )
    assert patched.status_code == 200
    assert patched.json()["issuer"] == "Coursera"

    assert client.delete(f"/api/v1/certificates/{cert_id}", headers=auth_headers).status_code == 204
    assert client.get("/api/v1/certificates", headers=auth_headers).json() == []
