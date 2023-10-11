from src.models.order import Menu
from src.models.users import User


async def event_01_ensure_indexes():
    await Menu.ensure_indexes()
    await User.ensure_indexes()

    print("index_created")


events = [v for k, v in locals().items() if k.startswith("event_")]
