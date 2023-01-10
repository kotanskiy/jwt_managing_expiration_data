from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.user.resource import UserResource
from domain.services import UserService
from domain.user.repository import IUserRepository
from infrastructure.mongo import get_mongo_database
from infrastructure.user.repository import UserRepositoryMongo


@lru_cache
def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_mongo_database)) -> IUserRepository:
    return UserRepositoryMongo(db.users)


@lru_cache
def get_user_service(repository: IUserRepository = Depends(get_user_repository)):
    return UserService(repository)


@lru_cache
def get_user_resource(service: UserService = Depends(get_user_service)):
    return UserResource(service)
