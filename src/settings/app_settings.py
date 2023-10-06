from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str

    class Config:
        extra = "ignore"


app_settings = Settings(_env_file=".env")
