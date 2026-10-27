import uuid
from typing import Any
from urllib.parse import urlparse

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings

ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


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

        parsed = urlparse(self.endpoint_raw)
        if parsed.scheme:
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
        normalized = content_type.lower().strip()
        if normalized not in ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(ALLOWED_IMAGE_TYPES.keys())
            raise ValueError(f"Invalid image type '{content_type}'. Allowed MIME types: {allowed}")
        return ALLOWED_IMAGE_TYPES[normalized]

    async def ensure_bucket_exists(self) -> None:
        async with self._get_client_context() as client:
            try:
                await client.head_bucket(Bucket=self.bucket_name)
            except ClientError:
                await client.create_bucket(Bucket=self.bucket_name)

    async def upload_image(
        self,
        file_data: bytes,
        content_type: str,
        prefix: str | None = None,
    ) -> tuple[str, str]:
        extension = self.validate_content_type(content_type)
        file_id = uuid.uuid4()
        filename = f"{file_id}{extension}"

        if prefix:
            clean_prefix = prefix.strip("/")
            key = f"{clean_prefix}/{filename}"
        else:
            key = filename

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
