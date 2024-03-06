from beanie import Document
from datetime import datetime
from pydantic import BaseModel


class Menu(Document):
    title: str
    link: str
    image_name: str

    class Settings:
        name = "menu"


class Item(BaseModel):
    name: str
    food: str
    price: int
    quantity: int


class Order(Document):
    title: str
    created_by: str
    created_at : datetime
    description: str
    namesAllowed: list[str]
    menu: str
    area: int
    share: bool
    order_date: datetime
    item_list: list[Item]

    class Settings:
        name = "order"


class ItemOrder(Document):
    created_at : datetime
    created_by: str
    order_id: str
    name: str
    food: str
    price : int
    quantity: int

    class Settings:
        name = "order_detail"



