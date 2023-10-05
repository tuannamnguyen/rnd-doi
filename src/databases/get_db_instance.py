from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks import MotorAsyncIOInstance


def get_db_instance(mongo_url: str, db_name: str):
    motor_client = AsyncIOMotorClient(mongo_url)[db_name]
    instance = MotorAsyncIOInstance(motor_client)
    return instance
