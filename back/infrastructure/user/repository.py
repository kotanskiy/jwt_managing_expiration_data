from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorCollection

from domain.profile.exceptions import UserNotFoundError
from domain.profile.models import Profile, Permission
from domain.profile.repository import IUserRepository


class UserRepositoryMongo(IUserRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    @staticmethod
    def _user_to_doc_adapter(user: Profile) -> dict:
        user_dict = user.dict()
        user_dict["_id"] = str(user.id)
        del user_dict["id"]
        return user_dict

    @staticmethod
    def _doc_to_user_adapter(user: dict) -> Profile:
        return Profile(
            id=user["_id"],
            username=user["username"],
            password_hash=user["password_hash"],
            bio=user["bio"],
            permissions=[Permission(name=p) for p in user["permissions"]]
        )

    async def create(self, user: Profile):
        await self._collection.insert_one(self._user_to_doc_adapter(user))

    async def update(self, user: Profile):
        await self._collection.update_one(
            {"_id": str(user.id)},
            {
                "$set": {
                    "bio": user.bio,
                    "permissions": [p.name for p in user.permissions],
                }
            },
        )

    async def retrieve(self, user_id: UUID) -> Profile:
        user_doc = await self._collection.find_one({"_id": str(user_id)})
        if user_doc is None:
            raise UserNotFoundError()
        return self._doc_to_user_adapter(user_doc)

    async def retrieve_by_username(self, username: str) -> Profile:
        user_doc = await self._collection.find_one({"username": username})
        if user_doc is None:
            raise UserNotFoundError()
        return self._doc_to_user_adapter(user_doc)
