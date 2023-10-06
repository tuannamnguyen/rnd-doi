from pydantic_settings import BaseSettings


class MinioSettings(BaseSettings):
    MINIO_HOST: str
    MINIO_PORT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool
    MINIO_BUCKET_LOCAL: str

    class Config:
        extra = "ignore"


minio_settings = MinioSettings(_env_file=".env")
