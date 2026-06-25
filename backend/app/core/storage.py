"""Pluggable blob storage for uploaded documents.

Two backends share one ``FileStorage`` protocol:

* :class:`LocalFileStorage` — writes bytes under a configured directory using
  opaque server-generated names (safe against path traversal). Fine for local
  development, but the filesystem is ephemeral on managed hosts.
* :class:`S3FileStorage` — stores bytes in an S3-compatible bucket (Cloudflare
  R2, AWS S3, etc.), which persists across redeploys.

The database always stores only metadata plus the opaque ``stored_filename``
(the object key). :func:`get_storage` picks the backend from configuration.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Protocol

from app.core.config import get_settings

settings = get_settings()


class FileStorage(Protocol):
    """Minimal interface every storage backend implements."""

    def save(self, content: bytes, *, suffix: str = "", content_type: str | None = None) -> str: ...

    def read(self, stored_filename: str) -> bytes: ...

    def exists(self, stored_filename: str) -> bool: ...

    def delete(self, stored_filename: str) -> None: ...


class LocalFileStorage:
    """Stores and retrieves bytes on the local filesystem."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.upload_dir)

    def _ensure_base_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, *, suffix: str = "", content_type: str | None = None) -> str:
        """Persist ``content`` and return its opaque stored filename."""
        self._ensure_base_dir()
        stored_filename = f"{uuid.uuid4().hex}{suffix}"
        (self.base_dir / stored_filename).write_bytes(content)
        return stored_filename

    def path_for(self, stored_filename: str) -> Path:
        """Resolve the on-disk path for a stored file, guarding traversal."""
        candidate = (self.base_dir / stored_filename).resolve()
        base = self.base_dir.resolve()
        if base not in candidate.parents:
            raise ValueError("Resolved path escapes the storage directory.")
        return candidate

    def read(self, stored_filename: str) -> bytes:
        return self.path_for(stored_filename).read_bytes()

    def exists(self, stored_filename: str) -> bool:
        return self.path_for(stored_filename).is_file()

    def delete(self, stored_filename: str) -> None:
        """Remove a stored file if it exists (idempotent)."""
        self.path_for(stored_filename).unlink(missing_ok=True)


class S3FileStorage:
    """Stores bytes in an S3-compatible bucket (Cloudflare R2 / AWS S3).

    ``boto3`` is imported lazily so the dependency is only touched when object
    storage is actually configured, keeping local/test runs free of it.
    """

    def __init__(self, prefix: str = "documents/") -> None:
        if not settings.s3_configured:  # pragma: no cover - guarded by factory
            raise RuntimeError("S3 storage is not configured.")
        self.bucket = settings.s3_bucket
        self.prefix = prefix

    def _client(self):  # type: ignore[no-untyped-def]
        import boto3  # lazy import; only needed when S3 is configured

        return boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
        )

    def _key(self, stored_filename: str) -> str:
        return f"{self.prefix}{stored_filename}"

    def save(self, content: bytes, *, suffix: str = "", content_type: str | None = None) -> str:
        stored_filename = f"{uuid.uuid4().hex}{suffix}"
        self._client().put_object(
            Bucket=self.bucket,
            Key=self._key(stored_filename),
            Body=content,
            ContentType=content_type or "application/octet-stream",
        )
        return stored_filename

    def read(self, stored_filename: str) -> bytes:
        response = self._client().get_object(Bucket=self.bucket, Key=self._key(stored_filename))
        body: bytes = response["Body"].read()
        return body

    def exists(self, stored_filename: str) -> bool:
        client = self._client()
        try:
            client.head_object(Bucket=self.bucket, Key=self._key(stored_filename))
            return True
        except client.exceptions.ClientError:
            return False

    def delete(self, stored_filename: str) -> None:
        self._client().delete_object(Bucket=self.bucket, Key=self._key(stored_filename))


def get_storage() -> FileStorage:
    """Return the configured storage backend (S3/R2 when set, else local)."""
    if settings.s3_configured:
        return S3FileStorage()
    return LocalFileStorage()
