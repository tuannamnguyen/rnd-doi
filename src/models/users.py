from umongo import Document, fields

from src.models.utils import db_instance


@db_instance.register
class User(Document):
    fullname = fields.StringField(required=True)
    username = fields.StringField(unique=True, required=True)
    password = fields.StringField(required=True)

    class Meta:
        collection_name = "users"
