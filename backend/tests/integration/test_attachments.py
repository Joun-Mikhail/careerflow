"""Integration tests for attachment endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

PDF_BYTES = b"%PDF-1.4 fake pdf content for testing"
PDF_TYPE = "application/pdf"


def _create_application(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post("/api/v1/applications", json={"role_title": "Engineer"}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _upload(
    client: TestClient,
    headers: dict[str, str],
    app_id: str,
    *,
    filename: str = "resume.pdf",
    content: bytes = PDF_BYTES,
    content_type: str = PDF_TYPE,
    kind: str = "resume",
):
    return client.post(
        f"/api/v1/applications/{app_id}/attachments",
        files={"file": (filename, content, content_type)},
        data={"kind": kind},
        headers=headers,
    )


def test_upload_pdf(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = _upload(client, auth_headers, app_id)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["kind"] == "resume"
    assert body["original_filename"] == "resume.pdf"
    assert body["size_bytes"] == len(PDF_BYTES)


def test_list_attachments(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _upload(client, auth_headers, app_id)
    listing = client.get(f"/api/v1/applications/{app_id}/attachments", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_download_returns_file_with_attachment_disposition(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app_id = _create_application(client, auth_headers)
    attachment = _upload(client, auth_headers, app_id).json()
    response = client.get(f"/api/v1/attachments/{attachment['id']}/download", headers=auth_headers)
    assert response.status_code == 200
    assert response.content == PDF_BYTES
    assert "attachment;" in response.headers["content-disposition"]
    assert response.headers["x-content-type-options"] == "nosniff"


def test_reject_unsupported_type(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = _upload(
        client,
        auth_headers,
        app_id,
        filename="evil.exe",
        content=b"MZ...",
        content_type="application/x-msdownload",
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_reject_empty_file(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = _upload(client, auth_headers, app_id, content=b"")
    assert response.status_code == 422


def test_upload_on_unowned_application_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = _upload(client, auth_headers, "00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_attachment(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    attachment = _upload(client, auth_headers, app_id).json()
    assert (
        client.delete(f"/api/v1/attachments/{attachment['id']}", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.get(
            f"/api/v1/attachments/{attachment['id']}/download", headers=auth_headers
        ).status_code
        == 404
    )


def test_attachment_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    attachment = _upload(client, auth_headers, app_id).json()
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "other3@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    response = client.get(f"/api/v1/attachments/{attachment['id']}/download", headers=other_headers)
    assert response.status_code == 404
