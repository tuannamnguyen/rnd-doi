from pydantic import BaseModel
from fastapi import Form


class CreateMenuSchema(BaseModel):
    title: str
    link: str

    @classmethod
    def as_form(cls, title: str = Form(...), link: str = Form(...)):
        return cls(title=title, link=link)
