---
name: file-upload
description: |
  파일 업로드, S3 연동, 이미지 처리를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# File Upload Skill

파일 업로드, S3 연동, 이미지 처리를 구현합니다.

## Triggers

- "파일 업로드", "file upload", "s3", "이미지 처리"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `storageType` | ❌ | local/s3 (기본: local) |

---

## Output

### File Storage Interface

```python
# app/domain/services/storage.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UploadedFile:
    """Uploaded file metadata."""

    filename: str
    content_type: str
    size: int
    url: str
    storage_path: str


class StorageService(ABC):
    """Abstract storage service interface."""

    @abstractmethod
    async def upload(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        folder: str = "",
    ) -> UploadedFile:
        """Upload a file."""
        ...

    @abstractmethod
    async def download(self, storage_path: str) -> bytes:
        """Download a file."""
        ...

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """Delete a file."""
        ...

    @abstractmethod
    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get URL for a file (signed URL for private files)."""
        ...

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Check if a file exists."""
        ...
```

### Local Storage Implementation

```python
# app/infrastructure/storage/local.py
import aiofiles
import aiofiles.os
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.domain.services.storage import StorageService, UploadedFile


class LocalStorageService(StorageService):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: str | None = None) -> None:
        self._base_path = Path(base_path or settings.UPLOAD_DIR)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def _get_storage_path(self, filename: str, folder: str = "") -> str:
        """Generate storage path with UUID prefix."""
        ext = Path(filename).suffix
        unique_name = f"{uuid4().hex}{ext}"
        if folder:
            return f"{folder}/{unique_name}"
        return unique_name

    def _get_full_path(self, storage_path: str) -> Path:
        """Get full filesystem path."""
        return self._base_path / storage_path

    async def upload(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        folder: str = "",
    ) -> UploadedFile:
        """Upload file to local filesystem."""
        storage_path = self._get_storage_path(filename, folder)
        full_path = self._get_full_path(storage_path)

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)

        return UploadedFile(
            filename=filename,
            content_type=content_type,
            size=len(content),
            url=f"/files/{storage_path}",
            storage_path=storage_path,
        )

    async def download(self, storage_path: str) -> bytes:
        """Download file from local filesystem."""
        full_path = self._get_full_path(storage_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete(self, storage_path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self._get_full_path(storage_path)

        if not full_path.exists():
            return False

        await aiofiles.os.remove(full_path)
        return True

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get URL for local file."""
        return f"/files/{storage_path}"

    async def exists(self, storage_path: str) -> bool:
        """Check if file exists."""
        return self._get_full_path(storage_path).exists()
```

### S3 Storage Implementation

```python
# app/infrastructure/storage/s3.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aioboto3
from botocore.config import Config

from app.core.config import settings
from app.domain.services.storage import StorageService, UploadedFile


class S3StorageService(StorageService):
    """AWS S3 storage implementation."""

    def __init__(
        self,
        bucket: str | None = None,
        region: str | None = None,
    ) -> None:
        self._bucket = bucket or settings.S3_BUCKET
        self._region = region or settings.AWS_REGION
        self._session = aioboto3.Session()
        self._config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator:
        """Get S3 client."""
        async with self._session.client(
            "s3",
            region_name=self._region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=self._config,
        ) as client:
            yield client

    def _get_storage_path(self, filename: str, folder: str = "") -> str:
        """Generate S3 key with UUID prefix."""
        from pathlib import Path
        from uuid import uuid4

        ext = Path(filename).suffix
        unique_name = f"{uuid4().hex}{ext}"
        if folder:
            return f"{folder}/{unique_name}"
        return unique_name

    async def upload(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        folder: str = "",
    ) -> UploadedFile:
        """Upload file to S3."""
        storage_path = self._get_storage_path(filename, folder)

        async with self._get_client() as client:
            await client.put_object(
                Bucket=self._bucket,
                Key=storage_path,
                Body=content,
                ContentType=content_type,
                # Optional: Set metadata
                Metadata={
                    "original-filename": filename,
                },
            )

        url = await self.get_url(storage_path)

        return UploadedFile(
            filename=filename,
            content_type=content_type,
            size=len(content),
            url=url,
            storage_path=storage_path,
        )

    async def download(self, storage_path: str) -> bytes:
        """Download file from S3."""
        async with self._get_client() as client:
            response = await client.get_object(
                Bucket=self._bucket,
                Key=storage_path,
            )
            async with response["Body"] as stream:
                return await stream.read()

    async def delete(self, storage_path: str) -> bool:
        """Delete file from S3."""
        from botocore.exceptions import ClientError
        import structlog

        logger = structlog.get_logger()

        async with self._get_client() as client:
            try:
                await client.delete_object(
                    Bucket=self._bucket,
                    Key=storage_path,
                )
                return True
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                await logger.awarning(
                    "S3 delete failed",
                    storage_path=storage_path,
                    error_code=error_code,
                    error=str(e),
                )
                if error_code == "NoSuchKey":
                    return False  # File doesn't exist
                raise  # Re-raise other S3 errors

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get presigned URL for S3 object."""
        async with self._get_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self._bucket,
                    "Key": storage_path,
                },
                ExpiresIn=expires_in,
            )
            return url

    async def exists(self, storage_path: str) -> bool:
        """Check if object exists in S3."""
        from botocore.exceptions import ClientError

        async with self._get_client() as client:
            try:
                await client.head_object(
                    Bucket=self._bucket,
                    Key=storage_path,
                )
                return True
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "404":
                    return False
                raise  # Re-raise other S3 errors

    async def get_upload_presigned_url(
        self,
        filename: str,
        content_type: str,
        folder: str = "",
        expires_in: int = 3600,
    ) -> tuple[str, str]:
        """Get presigned URL for direct upload.

        Returns:
            Tuple of (presigned_url, storage_path)
        """
        storage_path = self._get_storage_path(filename, folder)

        async with self._get_client() as client:
            url = await client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self._bucket,
                    "Key": storage_path,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return url, storage_path
```

### File Upload Service

```python
# app/application/services/file.py
import asyncio
from io import BytesIO
from typing import BinaryIO

import magic
from PIL import Image

import structlog

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.domain.services.storage import StorageService, UploadedFile

logger = structlog.get_logger()

# Allowed MIME types and extensions
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": [".pdf"],
    "application/msword": [".doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
}


class FileService:
    """File upload and processing service."""

    def __init__(
        self,
        storage: StorageService,
        max_size: int | None = None,
    ) -> None:
        self._storage = storage
        self._max_size = max_size or settings.MAX_UPLOAD_SIZE

    async def validate_file(
        self,
        content: bytes,
        filename: str,
        allowed_types: dict[str, list[str]] | None = None,
    ) -> str:
        """Validate file content and return MIME type.

        Raises:
            ValidationError: If file is invalid.
        """
        if len(content) > self._max_size:
            raise ValidationError(
                f"File too large. Max size: {self._max_size // (1024 * 1024)}MB"
            )

        # Detect MIME type from content (not extension)
        mime_type = await asyncio.to_thread(
            magic.from_buffer, content, mime=True
        )

        allowed = allowed_types or {**ALLOWED_IMAGE_TYPES, **ALLOWED_DOCUMENT_TYPES}

        if mime_type not in allowed:
            raise ValidationError(f"File type not allowed: {mime_type}")

        # Verify extension matches content
        from pathlib import Path

        ext = Path(filename).suffix.lower()
        if ext not in allowed.get(mime_type, []):
            raise ValidationError(
                f"File extension doesn't match content type: {ext} vs {mime_type}"
            )

        return mime_type

    async def upload_file(
        self,
        content: bytes,
        filename: str,
        folder: str = "uploads",
        allowed_types: dict[str, list[str]] | None = None,
    ) -> UploadedFile:
        """Upload a file with validation."""
        mime_type = await self.validate_file(content, filename, allowed_types)

        result = await self._storage.upload(
            filename=filename,
            content=content,
            content_type=mime_type,
            folder=folder,
        )

        await logger.ainfo(
            "File uploaded",
            filename=filename,
            size=len(content),
            storage_path=result.storage_path,
        )

        return result

    async def upload_image(
        self,
        content: bytes,
        filename: str,
        folder: str = "images",
        max_width: int | None = None,
        max_height: int | None = None,
        quality: int = 85,
    ) -> UploadedFile:
        """Upload an image with optional resizing."""
        # Validate as image
        mime_type = await self.validate_file(
            content, filename, ALLOWED_IMAGE_TYPES
        )

        # Resize if needed
        if max_width or max_height:
            content = await self._resize_image(
                content,
                max_width=max_width or 10000,
                max_height=max_height or 10000,
                quality=quality,
            )

        return await self._storage.upload(
            filename=filename,
            content=content,
            content_type=mime_type,
            folder=folder,
        )

    async def _resize_image(
        self,
        content: bytes,
        max_width: int,
        max_height: int,
        quality: int = 85,
    ) -> bytes:
        """Resize image to fit within max dimensions."""

        def resize() -> bytes:
            img = Image.open(BytesIO(content))

            # Calculate new size maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save to bytes
            output = BytesIO()
            img_format = img.format or "JPEG"
            img.save(output, format=img_format, quality=quality)
            return output.getvalue()

        return await asyncio.to_thread(resize)

    async def create_thumbnail(
        self,
        storage_path: str,
        width: int = 200,
        height: int = 200,
    ) -> UploadedFile:
        """Create thumbnail from existing image."""
        content = await self._storage.download(storage_path)

        def create_thumb() -> bytes:
            img = Image.open(BytesIO(content))
            img.thumbnail((width, height), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format="JPEG", quality=80)
            return output.getvalue()

        thumb_content = await asyncio.to_thread(create_thumb)

        # Upload thumbnail
        from pathlib import Path

        original_name = Path(storage_path).stem
        return await self._storage.upload(
            filename=f"{original_name}_thumb.jpg",
            content=thumb_content,
            content_type="image/jpeg",
            folder="thumbnails",
        )

    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file."""
        result = await self._storage.delete(storage_path)
        if result:
            await logger.ainfo("File deleted", storage_path=storage_path)
        return result
```

### Streaming Download for Large Files

```python
# app/infrastructure/storage/streaming.py
from typing import AsyncIterator

import aiofiles


async def stream_file(file_path: str, chunk_size: int = 64 * 1024) -> AsyncIterator[bytes]:
    """Stream file in chunks for memory-efficient downloads.

    Args:
        file_path: Path to the file
        chunk_size: Size of each chunk (default 64KB)

    Yields:
        File content in chunks
    """
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk


async def stream_s3_file(
    client,
    bucket: str,
    key: str,
    chunk_size: int = 64 * 1024,
) -> AsyncIterator[bytes]:
    """Stream S3 file in chunks.

    Args:
        client: S3 client
        bucket: S3 bucket name
        key: S3 object key
        chunk_size: Size of each chunk

    Yields:
        S3 object content in chunks
    """
    response = await client.get_object(Bucket=bucket, Key=key)
    async with response["Body"] as stream:
        while chunk := await stream.read(chunk_size):
            yield chunk
```

### File Upload Routes

```python
# app/api/v1/routes/files.py
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import ActiveUser
from app.api.v1.dependencies.file import FileSvc
from app.infrastructure.storage.streaming import stream_file
from app.schemas.file import FileResponse, PresignedUrlResponse

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    service: FileSvc = None,
    _: ActiveUser = None,
):
    """Upload a file."""
    content = await file.read()

    result = await service.upload_file(
        content=content,
        filename=file.filename or "unnamed",
        folder=folder,
    )

    return FileResponse(
        filename=result.filename,
        content_type=result.content_type,
        size=result.size,
        url=result.url,
        storage_path=result.storage_path,
    )


@router.post("/upload-image", response_model=FileResponse)
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form(default="images"),
    max_width: int | None = Form(default=None),
    max_height: int | None = Form(default=None),
    service: FileSvc = None,
    _: ActiveUser = None,
):
    """Upload an image with optional resizing."""
    content = await file.read()

    result = await service.upload_image(
        content=content,
        filename=file.filename or "unnamed",
        folder=folder,
        max_width=max_width,
        max_height=max_height,
    )

    return FileResponse(
        filename=result.filename,
        content_type=result.content_type,
        size=result.size,
        url=result.url,
        storage_path=result.storage_path,
    )


@router.post("/upload-multiple", response_model=list[FileResponse])
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    folder: str = Form(default="uploads"),
    service: FileSvc = None,
    _: ActiveUser = None,
):
    """Upload multiple files."""
    results = []

    for file in files:
        content = await file.read()
        result = await service.upload_file(
            content=content,
            filename=file.filename or "unnamed",
            folder=folder,
        )
        results.append(
            FileResponse(
                filename=result.filename,
                content_type=result.content_type,
                size=result.size,
                url=result.url,
                storage_path=result.storage_path,
            )
        )

    return results


@router.delete("/{storage_path:path}")
async def delete_file(
    storage_path: str,
    service: FileSvc,
    _: ActiveUser,
):
    """Delete a file."""
    deleted = await service.delete_file(storage_path)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return {"message": "File deleted"}


@router.get("/download/{storage_path:path}")
async def download_file_streaming(
    storage_path: str,
    service: FileSvc,
    _: ActiveUser,
):
    """Download a file using streaming for large files.

    Memory-efficient download that streams file in chunks.
    Supports both local storage and S3.
    """
    from pathlib import Path
    import mimetypes
    from app.core.config import settings
    from app.infrastructure.storage.streaming import stream_file, stream_s3_file

    filename = Path(storage_path).name
    content_type, _ = mimetypes.guess_type(filename)

    # Check storage type and stream accordingly
    if settings.STORAGE_TYPE == "s3":
        # S3 streaming download
        from app.infrastructure.storage.s3 import S3StorageService

        if not isinstance(service._storage, S3StorageService):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage configuration mismatch",
            )

        # Check if file exists in S3
        exists = await service._storage.exists(storage_path)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        async def s3_stream():
            """Stream S3 file using the storage service client."""
            async with service._storage._get_client() as client:
                async for chunk in stream_s3_file(
                    client,
                    service._storage._bucket,
                    storage_path,
                ):
                    yield chunk

        return StreamingResponse(
            s3_stream(),
            media_type=content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    else:
        # Local storage streaming download
        full_path = service._storage._get_full_path(storage_path)

        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        return StreamingResponse(
            stream_file(str(full_path)),
            media_type=content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
```

### File Schemas

```python
# app/schemas/file.py
from pydantic import BaseModel


class FileResponse(BaseModel):
    """File response schema."""

    filename: str
    content_type: str
    size: int
    url: str
    storage_path: str


class PresignedUrlResponse(BaseModel):
    """Presigned URL response for direct upload."""

    upload_url: str
    storage_path: str
    expires_in: int
```

### File Dependencies

```python
# app/api/v1/dependencies/file.py
from typing import Annotated

from fastapi import Depends

from app.application.services.file import FileService
from app.core.config import settings
from app.domain.services.storage import StorageService
from app.infrastructure.storage.local import LocalStorageService
from app.infrastructure.storage.s3 import S3StorageService


def get_storage_service() -> StorageService:
    """Get storage service based on configuration."""
    if settings.STORAGE_TYPE == "s3":
        return S3StorageService()
    return LocalStorageService()


def get_file_service(
    storage: StorageService = Depends(get_storage_service),
) -> FileService:
    """Get file service dependency."""
    return FileService(storage)


FileSvc = Annotated[FileService, Depends(get_file_service)]
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # File Upload
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
```

## Dependencies

```toml
# Add to pyproject.toml
dependencies = [
    # ... existing ...
    "aiofiles>=24.1.0",
    "aioboto3>=13.0.0",
    "pillow>=11.0.0",
    "python-magic>=0.4.27",
]
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
