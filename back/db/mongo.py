import motor.motor_asyncio

from conf import Settings, get_settings
from fastapi import Depends


def get_mongo_database(settings: Settings = Depends(get_settings)) -> motor.motor_asyncio.AsyncIOMotorDatabase:
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
    return client.jwt_managing_expiration_data
