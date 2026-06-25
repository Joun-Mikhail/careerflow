"""Integration tests for CV (document vault) endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

PDF_BYTES = b"%PDF-1.4 minimal test content"
PDF = "application/pdf"


def _upload(
    client: TestClient, headers: dict[str, str], name: str = "cv.pdf", **data: object
) -> dict:
    response = client.post(
        "/api/v1/cvs",
        files={"file": (name, PDF_BYTES, PDF)},
        data=data,
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_upload_lists_and_marks_first_default(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    body = _upload(client, auth_headers, title="Backend CV")
    assert body["title"] == "Backend CV"
    assert body["source"] == "uploaded"
    assert body["is_default"] is True  # first CV becomes default
    assert body["has_file"] is True

    listing = client.get("/api/v1/cvs", headers=auth_headers).json()
    assert len(listing) == 1


def test_rejects_unsupported_type(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/cvs",
        files={"file": ("cv.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 422  # ValidationError envelope


def test_download_returns_bytes(client: TestClient, auth_headers: dict[str, str]) -> None:
    cv_id = _upload(client, auth_headers)["id"]
    download = client.get(f"/api/v1/cvs/{cv_id}/download", headers=auth_headers)
    assert download.status_code == 200
    assert download.content == PDF_BYTES
    assert download.headers["X-Content-Type-Options"] == "nosniff"


def test_setting_default_moves_the_flag(client: TestClient, auth_headers: dict[str, str]) -> None:
    first = _upload(client, auth_headers, title="First")
    second = _upload(client, auth_headers, title="Second")
    assert first["is_default"] is True
    assert second["is_default"] is False

    client.patch(f"/api/v1/cvs/{second['id']}", json={"is_default": True}, headers=auth_headers)
    by_id = {c["id"]: c for c in client.get("/api/v1/cvs", headers=auth_headers).json()}
    assert by_id[second["id"]]["is_default"] is True
    assert by_id[first["id"]]["is_default"] is False


def test_delete_cv(client: TestClient, auth_headers: dict[str, str]) -> None:
    cv_id = _upload(client, auth_headers)["id"]
    assert client.delete(f"/api/v1/cvs/{cv_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/v1/cvs/{cv_id}/download", headers=auth_headers).status_code == 404
