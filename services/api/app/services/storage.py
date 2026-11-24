from contextlib import asynccontextmanager
from typing import AsyncIterator

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings


class S3Storage:
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._region = region
        self._session = aioboto3.Session()
        self._config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )

    @asynccontextmanager
    async def _client(self) -> AsyncIterator:
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
            config=self._config,
        ) as client:
            yield client

    async def ensure_bucket(self) -> None:
        """Создаёт бакет, если его нет."""
        async with self._client() as s3:
            try:
                await s3.head_bucket(Bucket=self._bucket)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code in ("404", "NoSuchBucket", "NotFound"):
                    await s3.create_bucket(Bucket=self._bucket)
                else:
                    raise

    async def upload_fileobj(
        self, key: str, fileobj, content_type: str
    ) -> None:
        """Загружает file-like объект в S3 по указанному ключу."""
        async with self._client() as s3:
            await s3.upload_fileobj(
                Fileobj=fileobj,
                Bucket=self._bucket,
                Key=key,
                ExtraArgs={"ContentType": content_type},
            )

    async def generate_presigned_url(
        self, key: str, expires_in: int | None = None
    ) -> str:
        """Возвращает временную ссылку на скачивание объекта."""
        async with self._client() as s3:
            return await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in
                or settings.s3.presigned_url_expire_seconds,
            )

    async def delete_file(self, key: str) -> None:
        async with self._client() as s3:
            await s3.delete_object(Bucket=self._bucket, Key=key)

    async def stream_object(self, key: str) -> AsyncIterator[bytes]:
        async with self._client() as s3:
            response = await s3.get_object(Bucket=self._bucket, Key=key)
            body = response["Body"]
            try:
                async for chunk in body.iter_chunks(chunk_size=65536):
                    yield chunk
            finally:
                body.close()


storage = S3Storage(
    endpoint_url=settings.s3.endpoint_url,
    access_key=settings.s3.access_key,
    secret_key=settings.s3.secret_key,
    bucket=settings.s3.bucket,
    region=settings.s3.region,
)
