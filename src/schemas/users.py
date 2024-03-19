from pydantic import BaseModel, field_validator


class UserSchema(BaseModel):
    fullname: str
    username: str
    area: int
    password: str
    confirm_password : str


class UpdateUserSchema(BaseModel):
    fullname : str
    area : int
