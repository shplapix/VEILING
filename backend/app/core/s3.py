import contextlib
import json
import uuid
from pathlib import Path
from typing import Any

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings

ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024


class S3Service:
    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
        public_url: str | None = None,
        use_ssl: bool | None = None,
    ) -> None:
        self.endpoint_raw = endpoint_url or settings.MINIO_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.bucket_name = bucket_name or settings.MINIO_BUCKET_NAME
        self.public_url = public_url or settings.MINIO_PUBLIC_URL
        self.use_ssl = settings.MINIO_USE_SSL if use_ssl is None else use_ssl

        if self.endpoint_raw.startswith(("http://", "https://")):
            self.endpoint_url = self.endpoint_raw
        else:
            protocol = "https" if self.use_ssl else "http"
            self.endpoint_url = f"{protocol}://{self.endpoint_raw}"

        self.session = aioboto3.Session()

    def _get_client_context(self) -> Any:
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1",
        )

    def get_public_url(self, key: str) -> str:
        base = self.public_url.rstrip("/")
        clean_key = key.lstrip("/")
        return f"{base}/{clean_key}"

    def validate_content_type(self, content_type: str) -> str:
        clean_type = content_type.split(";")[0].lower().strip()
        if clean_type not in ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_IMAGE_TYPES.keys()))
            raise ValueError(f"Invalid image type '{content_type}'. Allowed MIME types: {allowed}")
        return ALLOWED_IMAGE_TYPES[clean_type]

    def validate_image_size(self, size: int) -> None:
        if size <= 0:
            raise ValueError("Image file is empty")
        if size > MAX_IMAGE_SIZE_BYTES:
            max_mb = MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
            raise ValueError(f"Image size exceeds maximum allowed size of {max_mb}MB")

    def validate_image_bytes(self, file_data: bytes, content_type: str) -> None:
        if len(file_data) < 8:
            raise ValueError("Image file is too small to be a valid image")
        clean_type = content_type.split(";")[0].lower().strip()
        if clean_type in ("image/jpeg", "image/jpg"):
            if not file_data.startswith(b"\xff\xd8\xff"):
                raise ValueError("File content does not match JPEG image signature")
        elif clean_type == "image/png":
            if not file_data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("File content does not match PNG image signature")
        elif clean_type == "image/webp" and not (
            file_data.startswith(b"RIFF") and file_data[8:12] == b"WEBP"
        ):
            raise ValueError("File content does not match WebP image signature")

    def validate_image(self, file_data: bytes, content_type: str) -> str:
        extension = self.validate_content_type(content_type)
        self.validate_image_size(len(file_data))
        self.validate_image_bytes(file_data, content_type)
        return extension

    async def ensure_bucket_exists(self) -> None:
        async with self._get_client_context() as client:
            try:
                await client.head_bucket(Bucket=self.bucket_name)
            except ClientError:
                await client.create_bucket(Bucket=self.bucket_name)

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                    }
                ],
            }
            with contextlib.suppress(Exception):
                await client.put_bucket_policy(Bucket=self.bucket_name, Policy=json.dumps(policy))

    async def upload_image(
        self,
        file_data: bytes,
        content_type: str,
        prefix: str | None = None,
        filename: str | None = None,
    ) -> tuple[str, str]:
        extension = self.validate_content_type(content_type)
        if filename:
            file_name_clean = Path(filename).name
            if not file_name_clean.lower().endswith(extension):
                file_name_clean = f"{file_name_clean}{extension}"
        else:
            file_id = uuid.uuid4()
            file_name_clean = f"{file_id}{extension}"

        if prefix:
            clean_prefix = prefix.strip("/")
            key = f"{clean_prefix}/{file_name_clean}"
        else:
            key = file_name_clean

        async with self._get_client_context() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
            )

        return key, self.get_public_url(key)

    async def delete_image(self, key: str) -> None:
        async with self._get_client_context() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )

    async def get_image(self, key: str) -> tuple[bytes, str]:
        async with self._get_client_context() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            data: bytes = await response["Body"].read()
            content_type: str = response.get("ContentType", "application/octet-stream")
            return data, content_type


s3_service = S3Service()
