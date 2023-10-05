from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str


app_settings = Settings(_env_file="src/env/.env")
