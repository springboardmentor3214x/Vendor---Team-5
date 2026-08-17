"""Small API-layer adapter for storing uploaded document bytes locally.

Document lifecycle services own database versioning.  This module deliberately
only validates and persists bytes so the API routes can pass trusted metadata to
those services without duplicating lifecycle rules.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


ALLOWED_DOCUMENT_EXTENSIONS = frozenset(
    {"pdf", "xlsx", "xls", "docx", "doc", "png", "jpg", "jpeg", "zip"}
)
MAX_DOCUMENT_UPLOAD_BYTES = int(
    os.getenv("DOCUMENT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))
)
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"


@dataclass(frozen=True)
class StoredUpload:
    file_name: str
    file_path: str
    file_size: int
    content_type: str | None


async def store_document_upload(file: UploadFile, *, area: str) -> StoredUpload:
    """Validate and persist an uploaded file under the named document area."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="A document file is required")

    safe_name = Path(file.filename).name
    extension = Path(safe_name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported document file type",
        )

    directory = UPLOAD_ROOT / area
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{uuid4().hex}_{safe_name}"
    bytes_written = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > MAX_DOCUMENT_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Document file exceeds the 10 MB upload limit",
                    )
                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except OSError as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to store document") from error
    finally:
        await file.close()

    return StoredUpload(
        file_name=safe_name,
        file_path=str(destination),
        file_size=bytes_written,
        content_type=file.content_type,
    )
