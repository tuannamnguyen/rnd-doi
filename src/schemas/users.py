from pydantic import BaseModel, field_validator


class UserSchema(BaseModel):
    fullname: str
    username: str
    password: str
