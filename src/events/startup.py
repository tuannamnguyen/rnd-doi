from beanie import init_beanie


async def event_01_init_db():
    from src.settings.app_settings import app_settings
    from src.models.order import Menu, Order, ItemOrder, UserOrder
    from src.models.users import User
    from motor.motor_asyncio import AsyncIOMotorClient

    db_instance = AsyncIOMotorClient(app_settings.MONGODB_URL)
    await init_beanie(
        database=db_instance["rnd-doi"], document_models=[Menu, Order, User, ItemOrder, UserOrder]
    )


events = [v for k, v in locals().items() if k.startswith("event_")]
