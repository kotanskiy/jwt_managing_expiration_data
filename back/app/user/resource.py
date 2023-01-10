from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel

from domain.services import UserService
from domain.user.exceptions import UserNotFoundError
from domain.user.models import User


class UserResponse(BaseModel):
    id: UUID
    username: str
    bio: str
    permissions: list[str]

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return UserResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            permissions=[perm.name for perm in user.permissions]
        )


class UserResource:
    def __init__(
        self,
        service: UserService,
    ):
        self._service = service

    async def retrieve(self, user_id: UUID) -> UserResponse:
        user = await self._service.retrieve(user_id)
        return UserResponse.from_user(user)

    async def update(self, user_id: UUID, bio: str) -> dict:
        try:
            await self._service.update_bio(user_id, bio)
        except UserNotFoundError as err:
            raise HTTPException(status_code=404, detail=err.message)
        return {}
