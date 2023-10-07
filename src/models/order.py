from src.models.utils import db_instance
from umongo import Document, fields


@db_instance.register
class Order(Document):
    title = fields.StringField()
    description = fields.StringField()
    menu = fields.StringField()
    area = fields.IntegerField()
    share = fields.BooleanField()
    time_order = fields.DateTimeField()
    participants = fields.ListField(fields.StringField())
    item = fields.StringField()

    class Meta:
        collection_name = "order"


@db_instance.register
class Menu(Document):
    title = fields.StringField()
    link = fields.StringField(unique=True)
    image_name = fields.StringField()

    class Meta:
        collection_name = "menu"
