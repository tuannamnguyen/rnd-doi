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


class CreateItemSchema(BaseModel):
    name: str
    food: str
    price: int
    quantity: int


class CreateOrderSchema(BaseModel):
    title: str
    description: str
    owner: str
    namesAllowed: list[str]
    menu: str
    area: int
    share: bool
    item_list: list[CreateItemSchema]
    tags: list[str]

    @field_validator("area")
    def validate_area(cls, v: int):
        if v != 1 and v != 2:
            raise ErrorResponseException(**get_error_code(4000103))
        return v

    # @field_validator("item_list")
    # def validate_item_list(cls, v: list[CreateItemSchema]):
    #     if len(v) == 0:
    #         raise ErrorResponseException(**get_error_code(4000104))
    #     return v


class GetMenuImageSchema(BaseModel):
    image_name: str


class AddNewItemSchema(BaseModel):
    new_item: list[CreateItemSchema]
    order: CreateOrderSchema
