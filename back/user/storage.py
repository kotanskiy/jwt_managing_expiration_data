from functools import lru_cache
from typing import Optional
from uuid import UUID
from abc import ABC, abstractmethod

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

from db.mongo import get_mongo_database


class User(BaseModel):
    id: UUID
    username: str
    password_hash: str
    bio: str

    @classmethod
    def from_mongo_doc(cls, doc: dict) -> "User":
        return cls(
            id=UUID(doc["_id"]),
            username=doc["username"],
            password_hash=doc["password_hash"],
            bio=doc["bio"],
        )


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def retrieve(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def retrieve_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def update_bio(self, user_id: UUID, bio: str) -> User:
        pass


class UserRepositoryMongo(IUserRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    @staticmethod
    def _to_mongo_doc(user: User) -> dict:
        user_dict = user.dict()
        user_dict["_id"] = str(user.id)
        del user_dict["id"]
        return user_dict

    async def save(self, user: User):
        await self._collection.insert_one(self._to_mongo_doc(user))

    async def retrieve(self, user_id: UUID) -> Optional[User]:
        user_doc = await self._collection.find_one({"_id": str(user_id)})
        if user_doc is None:
            return None
        return User.from_mongo_doc(user_doc)

    async def retrieve_by_username(self, username: str) -> Optional[User]:
        user_doc = await self._collection.find_one({"username": username})
        if user_doc is None:
            return None
        return User.from_mongo_doc(user_doc)

    async def update_bio(self, user_id: UUID, bio: str) -> User:
        await self._collection.update_one(
            {"_id": str(user_id)},
            {"$set": {"bio": bio}},
        )
        return await self.retrieve(user_id)


class UserRepositoryLocal(IUserRepository):
    _storage = None

    def __new__(cls, *args, **kwargs):
        if cls._storage is None:
            cls._storage = super().__new__(cls, *args, **kwargs)
        return cls._storage

    def __init__(self):
        self._docs = {}
        self._username_index = {}

    def save(self, user: User):
        self._docs[user.id] = user
        self._username_index[user.username] = user.id

    def retrieve(self, user_id: UUID) -> Optional[User]:
        return self._docs.get(user_id)

    def retrieve_by_username(self, username: str) -> Optional[User]:
        user_id = self._username_index.get(username)
        if user_id is None:
            return None
        return self.retrieve(user_id)

    def update_bio(self, user_id: UUID, bio: str) -> User:
        user = self._docs[user_id]
        user.bio = bio
        return user


@lru_cache
def get_user_storage(db: AsyncIOMotorDatabase = Depends(get_mongo_database)) -> IUserRepository:
    return UserRepositoryMongo(db.users)
