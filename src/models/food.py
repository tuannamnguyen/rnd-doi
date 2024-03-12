from beanie import Document, Indexed
from datetime import datetime
from pydantic import BaseModel

class Food(Document):
    image_url : str
    food_name : str
    price: int
    ingredients : list[str]
    class Settings:
        name = "food"