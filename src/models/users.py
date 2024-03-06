from beanie import Document, Indexed


class User(Document):
    fullname: str
    username: Indexed(str, unique=True) # type: ignore
    password: str
    role : str
    area : int

    class Settings:
        name = "users"
