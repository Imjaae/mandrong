from __future__ import annotations

import hashlib
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import get_settings


SUPPORTED_IMAGE_MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def storage_root() -> Path:
    root = get_settings().storage_root
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def ensure_storage_dirs() -> None:
    for name in ["uploads", "generated", "annotations", "exports"]:
        (storage_root() / name).mkdir(parents=True, exist_ok=True)


async def save_upload(project_id: uuid.UUID, upload: UploadFile, kind: str) -> dict:
    ensure_storage_dirs()
    suffix = SUPPORTED_IMAGE_MIME.get(upload.content_type or "")
    if suffix is None:
        raise ValueError("UNSUPPORTED_FILE_TYPE")

    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    content = await upload.read()
    if len(content) > max_bytes:
        raise ValueError("UPLOAD_TOO_LARGE")

    width = height = None
    try:
        with Image.open(BytesIO(content)) as image:
            image = ImageOps.exif_transpose(image)
            image.load()
            width, height = image.size
    except (UnidentifiedImageError, OSError):
        raise ValueError("UNSUPPORTED_FILE_TYPE") from None

    digest = hashlib.sha256(content).hexdigest()
    relative = Path("uploads") / str(project_id) / f"{uuid.uuid4()}{suffix}"
    path = storage_root() / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

    return {
        "storage_path": str(relative),
        "mime_type": upload.content_type or "application/octet-stream",
        "size_bytes": len(content),
        "width": width,
        "height": height,
        "checksum": digest,
        "content": content,
        "original_filename": upload.filename,
    }


def full_path(storage_path: str) -> Path:
    return storage_root() / storage_path
