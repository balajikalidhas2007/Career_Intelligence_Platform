"""Local filesystem storage backend.

Stores files under settings.local_storage_path, organized by user_id.
Each file gets a UUID-based name to avoid collisions.
"""

import uuid
from pathlib import Path

import aiofiles

from app.config import settings


async def save_file(user_id: uuid.UUID, filename: str, content: bytes) -> str:
    """Save file content and return the storage key.

    The storage key is a relative path like: <user_id>/<uuid>_<sanitized_filename>
    """
    safe_name = Path(filename).name  # strip directory components
    storage_name = f"{uuid.uuid4().hex}_{safe_name}"
    relative_key = f"{user_id}/{storage_name}"

    base = Path(settings.local_storage_path)
    dest_dir = base / str(user_id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / storage_name
    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    return relative_key


async def read_file(storage_key: str) -> bytes:
    """Read file content by storage key."""
    path = Path(settings.local_storage_path) / storage_key
    if not path.exists():
        raise FileNotFoundError(f"File not found: {storage_key}")
    async with aiofiles.open(path, "rb") as f:
        return await f.read()


async def delete_file(storage_key: str) -> None:
    """Delete a file by storage key. Silently ignores missing files."""
    path = Path(settings.local_storage_path) / storage_key
    if path.exists():
        path.unlink()
