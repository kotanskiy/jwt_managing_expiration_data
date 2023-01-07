from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Depends
from pydantic import BaseModel

from conf import Settings, get_settings


class Payload(BaseModel):
    sub: str
    username: str
    exp: datetime


class JWTService:
    def __init__(
        self,
        access_secret: str,
        refresh_secret: str,
        access_max_age: int,
        refresh_max_age: int,
    ):
        self._access_secret = access_secret
        self._refresh_secret = refresh_secret
        self._access_max_age = access_max_age
        self._refresh_max_age = refresh_max_age

    @staticmethod
    def _generate_token(user_id: UUID, username: str, secret: str, expiration_seconds: int) -> str:
        payload = Payload(
            sub=str(user_id),
            username=username,
            exp=datetime.now(tz=timezone.utc) + timedelta(seconds=expiration_seconds),
        )
        return jwt.encode(payload.dict(), secret, algorithm="HS256")

    def generate_tokens(self, user_id: UUID, username: str) -> tuple[str, str]:
        """
        :return: access_token, refresh_token
        """
        access = self._generate_token(user_id, username, self._access_secret, self._access_max_age)
        refresh = self._generate_token(user_id, username, self._refresh_secret, self._refresh_max_age)
        return access, refresh

    def verify_access_token(self, token: str) -> Optional[Payload]:
        return self._verify(token, self._access_secret)

    def verify_refresh_token(self, token: str) -> Optional[Payload]:
        return self._verify(token, self._refresh_secret)

    @staticmethod
    def _verify(token: str, secret: str) -> Optional[Payload]:
        try:
            payload: dict = jwt.decode(
                token,
                secret,
                algorithms="HS256",
            )
            return Payload(**payload)
        except jwt.InvalidTokenError:
            return None


def get_jwt_service(settings: Settings = Depends(get_settings)):
    return JWTService(
        access_secret=settings.jwt_access_secret,
        refresh_secret=settings.jwt_refresh_secret,
        access_max_age=settings.jwt_access_max_age,
        refresh_max_age=settings.jwt_refresh_max_age,
    )
