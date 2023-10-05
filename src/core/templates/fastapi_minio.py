# -*- coding: utf-8 -*-

import logging
from io import BytesIO

from src.core.patterns.singleton import Singleton
from src.constants.logger import CONSOLE_LOGGER_NAME
from src.constants.image import MAX_SIZE
from minio import Minio
from minio.error import S3Error
from src.settings.minio_settings import minio_settings


class MinIOHandler(metaclass=Singleton):
    def __init__(self, *args, **kwargs) -> None:

        self.logger = logging.getLogger(CONSOLE_LOGGER_NAME)
        self.host = minio_settings.MINIO_HOST
        self.port = minio_settings.MINIO_PORT
        self.access_key = minio_settings.MINIO_ACCESS_KEY
        self.secret_key = minio_settings.MINIO_SECRET_KEY
        self.secure = minio_settings.MINIO_SECURE
        self.bucket = minio_settings.MINIO_BUCKET_LOCAL

        try:
            self.client = Minio(
                f"{self.host}:{self.port}",
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
            found = self.client.bucket_exists(self.bucket)

            if not found:
                self.client.make_bucket(self.bucket)
                self.logger.info(f"Bucket {self.bucket} created new")
            else:
                self.logger.warning(f"Bucket {self.bucket} already exists")

        except S3Error as e:
            self.logger.error(f"Try to connect MinIO get exception {e.message}")

    async def get_object(self, name: str):
        try:
            minio_object = self.client.get_object(self.bucket, name)
        except Exception:
            self.logger.critical("Cannot get object from minio")
            return
        else:
            return minio_object

    async def get_url(self, name: str):
        try:
            object_url = self.client.presigned_get_object(self.bucket, name)
        except Exception:
            self.logger.critical("Cannot get object's url from minio")
            return
        else:
            return object_url

    async def put_object(self, file_minio_path: str, data: BytesIO):
        try:
            upload_response = self.client.put_object(
                self.bucket, file_minio_path, data=data, length=-1, part_size=MAX_SIZE
            )
        except Exception:
            self.logger.critical("Cannot upload file minio")
            return
        else:
            return upload_response


minio_client = MinIOHandler()
