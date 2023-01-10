from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .models import User


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User):
        pass

    @abstractmethod
    async def update(self, user: User):
        pass

    @abstractmethod
    async def retrieve(self, user_id: UUID) -> User:
        pass

    @abstractmethod
    async def retrieve_by_username(self, username: str) -> User:
        pass
