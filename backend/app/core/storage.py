"""Local filesystem storage for uploaded attachments.

Files are written under a configured directory that lives outside any
statically-served path, using opaque server-generated names so the original
filename can never influence the storage location (preventing path traversal).
The database stores only metadata plus the opaque ``stored_filename``.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class LocalFileStorage:
    """Stores and retrieves attachment bytes on the local filesystem."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.upload_dir)

    def _ensure_base_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, *, suffix: str = "") -> str:
        """Persist ``content`` and return its opaque stored filename."""
        self._ensure_base_dir()
        stored_filename = f"{uuid.uuid4().hex}{suffix}"
        (self.base_dir / stored_filename).write_bytes(content)
        return stored_filename

    def path_for(self, stored_filename: str) -> Path:
        """Resolve the on-disk path for a stored file, guarding traversal."""
        # ``stored_filename`` is always server-generated, but resolve and verify
        # containment as defence in depth.
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
        path = self.path_for(stored_filename)
        path.unlink(missing_ok=True)
