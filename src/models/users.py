from beanie import Document, Indexed


class User(Document):
    fullname: str
    username: Indexed(str, unique=True)
    password: str

    class Settings:
        name = "users"
