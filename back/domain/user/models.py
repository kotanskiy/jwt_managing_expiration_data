import hashlib
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class Permission(BaseModel):
    name: str

    def __eq__(self, other: "Permission") -> bool:
        return self.name == other.name


class User(BaseModel):
    id: UUID
    username: str
    password_hash: str
    bio: str = ""
    permissions: list[Permission] = []

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def create(cls, username: str, password: str) -> "User":
        return cls(
            id=uuid4(),
            username=username,
            password_hash=cls._hash(password),
        )

    def verify_password(self, password: str) -> bool:
        return self.password_hash == self._hash(password)

    def update_bio(self, bio: str):
        self.bio = bio

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
