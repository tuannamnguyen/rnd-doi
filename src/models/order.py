from src.models.utils import db_instance
from umongo import Document, fields


@db_instance.register
class Order(Document):
    class Meta:
        collection_name = "order"


@db_instance.register
class Menu(Document):
    title = fields.StringField()
    link = fields.StringField()
    image = fields.StringField()

    class Meta:
        collection_name = "menu"
