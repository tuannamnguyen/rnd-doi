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
class Order(Document):
    title = fields.StringField()
    description = fields.StringField()
    namesAllowed = fields.ListField(fields.StringField())
    owner = fields.StringField()
    menu = fields.StringField()
    area = fields.IntegerField()
    share = fields.BooleanField()
    order_date = fields.DateTimeField()
    item_list = fields.ListField(
        fields.DictField(
            name=fields.StringField(),
            food=fields.StringField(),
            price=fields.IntegerField(),
            quantity=fields.IntegerField(),
        )
    )
    tags = fields.ListField(fields.StringField())

    class Meta:
        collection_name = "order"
