from pydantic import BaseModel
class food_schema(BaseModel):
    image_url : str
    food_name : str
    price: int
    ingredients : list = []
