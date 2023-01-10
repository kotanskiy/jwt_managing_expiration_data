from uuid import UUID

from fastapi import Response, HTTPException
from jwt import InvalidTokenError

from app.auth.jwt import JWTService
from app.user.resource import UserResponse
from conf import Settings
from domain.services import UserService, UserAlreadyExistsError
from domain.user.exceptions import UserNotFoundError
from domain.user.models import User


AUTH_ERROR_MSG = "Authentication failed"


class AuthResource:
    def __init__(self, jwt_service: JWTService, user_service: UserService, settings: Settings):
        self._jwt_service = jwt_service
        self._user_service = user_service
        self._access_max_age = settings.jwt_access_max_age
        self._refresh_max_age = settings.jwt_refresh_max_age

    def _set_auth_cookies(self, response: Response, user_id: str, username: str, permissions: list[str]):
        access_token, refresh_token = self._jwt_service.generate_tokens(user_id, username, permissions)
        response.set_cookie("accessToken", access_token, httponly=True, secure=True, max_age=self._access_max_age)
        response.set_cookie("refreshToken", refresh_token, httponly=True, secure=True, max_age=self._refresh_max_age)

    def _set_user_auth_cookies(self, user: User, response: Response):
        self._set_auth_cookies(response, str(user.id), user.username, [p.name for p in user.permissions])

    async def login(self, username: str, password: str, response: Response) -> UserResponse:
        try:
            user = await self._user_service.retrieve_by_username(username)
        except UserNotFoundError:
            raise HTTPException(status_code=401, detail=AUTH_ERROR_MSG)
        if not user.verify_password(password):
            raise HTTPException(status_code=401, detail=AUTH_ERROR_MSG)

        self._set_user_auth_cookies(user, response)
        return UserResponse.from_user(user)

    async def refresh(self, refresh_token: str, response: Response) -> UserResponse:
        try:
            payload = self._jwt_service.verify_refresh_token(refresh_token)
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail=AUTH_ERROR_MSG)
        user = await self._user_service.retrieve(UUID(payload.sub))
        self._set_user_auth_cookies(user, response)
        return UserResponse.from_user(user)

    async def registration(self, username: str, password: str, response: Response) -> UserResponse:
        try:
            user = await self._user_service.create(username, password)
        except UserAlreadyExistsError as err:
            raise HTTPException(status_code=400, detail=err.message)
        self._set_user_auth_cookies(user, response)
        return UserResponse.from_user(user)

    @staticmethod
    def logout(response: Response) -> dict:
        response.set_cookie("accessToken", "", httponly=True, secure=True, max_age=0)
        response.set_cookie("refreshToken", "", httponly=True, secure=True, max_age=0)
        return {}
