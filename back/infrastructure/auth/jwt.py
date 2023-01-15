from datetime import datetime, timezone, timedelta

import jwt
from pydantic import BaseModel


class Payload(BaseModel):
    sub: str
    username: str
    permissions: list[str]
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
    def _generate_token(user_id: str, username: str, permissions: list[str], secret: str, expiration_seconds: int) -> str:
        payload = Payload(
            sub=user_id,
            username=username,
            permissions=permissions,
            exp=datetime.now(tz=timezone.utc) + timedelta(seconds=expiration_seconds),
        )
        return jwt.encode(payload.dict(), secret, algorithm="HS256")

    def generate_tokens(self, user_id: str, username: str, permissions: list[str]) -> tuple[str, str]:
        """
        :return: access_token, refresh_token
        """
        access = self._generate_token(user_id, username, permissions, self._access_secret, self._access_max_age)
        refresh = self._generate_token(user_id, username, permissions, self._refresh_secret, self._refresh_max_age)
        return access, refresh

    def verify_access_token(self, token: str) -> Payload:
        return self._verify(token, self._access_secret)

    def verify_refresh_token(self, token: str) -> Payload:
        return self._verify(token, self._refresh_secret)

    @staticmethod
    def _verify(token: str, secret: str) -> Payload:
        """
        :raises InvalidTokenError
        """
        payload: dict = jwt.decode(
            token,
            secret,
            algorithms="HS256",
        )
        return Payload(**payload)
