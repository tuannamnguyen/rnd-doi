from src.models.utils import db_instance
from umongo import Document, fields


@db_instance.register
class Menu(Document):
    title = fields.StringField(unique=True)
    link = fields.StringField(unique=True)
    image_name = fields.StringField()

    class Meta:
        collection_name = "menu"


@db_instance.register
class Item(Document):
    menu = fields.StringField()
    name = fields.ListField(fields.StringField())
    food = fields.StringField()
    price = fields.IntegerField()
    quantity = fields.IntegerField()
    total = fields.IntegerField()

    class Meta:
        collection_name = "item"


@db_instance.register
class Order(Document):
    title = fields.StringField()
    description = fields.StringField()
    menu = fields.StringField()
    area = fields.IntegerField()
    share = fields.BooleanField()
    order_date = fields.DateTimeField()
    item_list = fields.ListField(fields.ReferenceField("Item"))
