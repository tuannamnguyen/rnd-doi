from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET: str
    ALGORITHM: str

    class Config:
        extra = "ignore"


auth_settings = AuthSettings(_env_file=".env")
