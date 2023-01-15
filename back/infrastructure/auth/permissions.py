from enum import Enum

from fastapi import HTTPException


class Permissions(str, Enum):
    PERMISSIONS_LIST = "read_permissions"

    def verify_permission(self, user_permissions: list[str]):
        if self.value not in user_permissions:
            raise HTTPException(status_code=403, detail="Permission denied")

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda p: p.value, cls._member_map_.values()))
