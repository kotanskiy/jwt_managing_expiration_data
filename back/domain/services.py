from uuid import UUID

from domain.user.exceptions import UserError, UserNotFoundError
from domain.user.models import User, Permission
from domain.user.repository import IUserRepository


class UserAlreadyExistsError(UserError):
    message = "User already exists"


class UserService:
    def __init__(self, repository: IUserRepository):
        self._repository = repository

    async def create(self, username: str, password: str) -> User:
        try:
            user = await self._repository.retrieve_by_username(username)
            if user:
                raise UserAlreadyExistsError()
        except UserNotFoundError:
            user = User.create(username, password)
        await self._repository.create(user)
        return user

    async def update_bio(self, user_id: UUID, bio: str):
        user = await self.retrieve(user_id)
        user.update_bio(bio)
        await self._repository.update(user)

    async def retrieve(self, user_id: UUID) -> User:
        return await self._repository.retrieve(user_id)

    async def retrieve_by_username(self, username: str) -> User:
        return await self._repository.retrieve_by_username(username)

    async def add_permission_to_user(self, user_id: UUID, permission_name: str):
        user = await self.retrieve(user_id)
        user.add_permission(Permission(name=permission_name))
        await self._repository.update(user)

    async def remove_permission_from_user(self, user_id: UUID, permission_name: str):
        user = await self.retrieve(user_id)
        user.remove_permission(Permission(name=permission_name))
        await self._repository.update(user)
