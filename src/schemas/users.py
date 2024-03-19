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

class UpdatePasswordSchema(BaseModel):
    old_password : str
    new_password : str
    confirm_password : str
