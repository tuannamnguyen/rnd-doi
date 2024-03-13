from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Food(Document):
    food_name : str
    price: int
    ingredients : list[str]
    menu_id : str
    image_url : str
    class Settings:
        name = "food"