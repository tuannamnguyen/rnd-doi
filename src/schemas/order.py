from pydantic import BaseModel, field_validator
from fastapi import Form
from datetime import datetime
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code


class CreateMenuSchema(BaseModel):
    title: str
    link: str

    @classmethod
    def as_form(cls, title: str = Form(...), link: str = Form(...)):
        return cls(title=title, link=link)


class CreateOrderSchema(BaseModel):
    title: str
    description: str
    menu: str
    area: int
    share: bool
    time_order: datetime = datetime.utcnow()
    participants: list[str] = []
    item: str

    @field_validator("area")
    def vaildate_area(cls, v: int):
        if v != 1 and v != 2:
            raise ErrorResponseException(**get_error_code(4000103))
        return v

    @field_validator("participants")
    def validate_participants_list(cls, v: list[str]):
        if len(v) == 0:
            raise ErrorResponseException(**get_error_code(4000104))
        return v
