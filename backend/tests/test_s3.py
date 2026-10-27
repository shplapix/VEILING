from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.core.s3 import S3Service
from tests.conftest import FakeS3Service


def test_allowed_mime_types() -> None:
    service = S3Service()
    assert service.validate_content_type("image/jpeg") == ".jpg"
    assert service.validate_content_type("IMAGE/JPEG") == ".jpg"
    assert service.validate_content_type("image/jpg") == ".jpg"
    assert service.validate_content_type("image/jpeg; charset=utf-8") == ".jpg"
    assert service.validate_content_type("image/png") == ".png"
    assert service.validate_content_type("image/webp") == ".webp"

    for invalid in ["application/pdf", "image/gif", "text/plain", "video/mp4"]:
        with pytest.raises(ValueError, match="Invalid image type"):
            service.validate_content_type(invalid)


def test_public_url_formatting() -> None:
    service = S3Service(
        public_url="https://s3.eu-central-1.amazonaws.com/archive-lots/",
    )
    url = service.get_public_url("test_image.jpg")
    assert url == "https://s3.eu-central-1.amazonaws.com/archive-lots/test_image.jpg"

    url_with_leading_slash = service.get_public_url("/nested/test_image.png")
    assert (
        url_with_leading_slash
        == "https://s3.eu-central-1.amazonaws.com/archive-lots/nested/test_image.png"
    )


def test_s3_service_endpoint_url_protocol() -> None:
    svc_http = S3Service(endpoint_url="localhost:9000", use_ssl=False)
    assert svc_http.endpoint_url == "http://localhost:9000"

    svc_https = S3Service(endpoint_url="localhost:9000", use_ssl=True)
    assert svc_https.endpoint_url == "https://localhost:9000"

    svc_explicit = S3Service(endpoint_url="https://minio.custom.io:9000")
    assert svc_explicit.endpoint_url == "https://minio.custom.io:9000"


async def test_fake_s3_upload_and_retrieve(fake_s3: FakeS3Service) -> None:
    sample_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    content_type = "image/jpeg"

    key, url = await fake_s3.upload_image(
        file_data=sample_bytes,
        content_type=content_type,
        prefix="lots/test-lot-123",
    )

    assert key.startswith("lots/test-lot-123/")
    assert key.endswith(".jpg")
    assert url == f"http://localhost:9000/archive-lots/{key}"

    retrieved_data, retrieved_type = await fake_s3.get_image(key)
    assert retrieved_data == sample_bytes
    assert retrieved_type == content_type

    await fake_s3.delete_image(key)
    with pytest.raises(ClientError):
        await fake_s3.get_image(key)


async def test_fake_s3_invalid_type_raises(fake_s3: FakeS3Service) -> None:
    with pytest.raises(ValueError, match="Invalid image type"):
        await fake_s3.upload_image(
            file_data=b"fake data",
            content_type="text/html",
        )


async def test_real_s3_service_lifecycle_mocked() -> None:
    svc = S3Service(
        endpoint_url="http://mock-minio:9000",
        bucket_name="test-bucket",
        public_url="http://mock-minio:9000/test-bucket",
    )

    mock_client = AsyncMock()
    mock_client.head_bucket = AsyncMock()
    mock_client.put_object = AsyncMock()
    mock_client.delete_object = AsyncMock()
    mock_body = AsyncMock()
    mock_body.read = AsyncMock(return_value=b"test-bytes-content")
    mock_client.get_object = AsyncMock(
        return_value={"Body": mock_body, "ContentType": "image/webp"}
    )

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch.object(svc, "_get_client_context", return_value=mock_ctx):
        await svc.ensure_bucket_exists()
        mock_client.head_bucket.assert_awaited_once_with(Bucket="test-bucket")

        key, url = await svc.upload_image(
            file_data=b"test-bytes-content",
            content_type="image/webp",
            prefix="lots/abc",
        )
        assert key.startswith("lots/abc/")
        assert key.endswith(".webp")
        assert url == f"http://mock-minio:9000/test-bucket/{key}"
        mock_client.put_object.assert_awaited_once()

        data, ctype = await svc.get_image(key)
        assert data == b"test-bytes-content"
        assert ctype == "image/webp"

        await svc.delete_image(key)
        mock_client.delete_object.assert_awaited_once_with(
            Bucket="test-bucket",
            Key=key,
        )


async def test_real_s3_service_ensure_bucket_creates_on_missing() -> None:
    svc = S3Service(
        endpoint_url="http://mock-minio:9000",
        bucket_name="missing-bucket",
    )

    mock_client = AsyncMock()
    mock_client.head_bucket = AsyncMock(
        side_effect=ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "HeadBucket",
        )
    )
    mock_client.create_bucket = AsyncMock()

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch.object(svc, "_get_client_context", return_value=mock_ctx):
        await svc.ensure_bucket_exists()
        mock_client.create_bucket.assert_awaited_once_with(Bucket="missing-bucket")
