from fastapi import Form
from pydantic import BaseModel
class food_schema(BaseModel):
    food_name : str
    price: int
    ingredients : list = []
    menu_id : str

    @classmethod
    def as_form(cls, food_name: str = Form(...), price: int = Form(...), ingredients: list[str] = Form(...), menu_id: str = Form(...)):
        return cls(food_name=food_name, price=price, ingredients=ingredients, menu_id=menu_id)
