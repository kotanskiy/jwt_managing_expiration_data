from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .models import Profile


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: Profile):
        pass

    @abstractmethod
    async def update(self, user: Profile):
        pass

    @abstractmethod
    async def retrieve(self, user_id: UUID) -> Profile:
        pass

    @abstractmethod
    async def retrieve_by_username(self, username: str) -> Profile:
        pass
