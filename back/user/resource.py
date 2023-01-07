import hashlib
from uuid import uuid4, UUID

from fastapi import HTTPException, Depends, Response
from pydantic import BaseModel

from user.storage import IUserRepository, User, get_user_storage
from auth.jwt import JWTService, get_jwt_service
from conf.settings import Settings, get_settings


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


class UserResponse(BaseModel):
    username: str
    bio: str


AUTH_ERROR_MSG = "Not authenticated"


class UserResource:
    def __init__(
        self,
        storage: IUserRepository,
        jwt_service: JWTService,
        access_max_age: int,
        refresh_max_age: int,
    ):
        self._storage = storage
        self._jwt_service = jwt_service
        self._access_max_age = access_max_age
        self._refresh_max_age = refresh_max_age

    def _set_auth_cookies(self, response: Response, user_id: UUID, username: str):
        access_token, refresh_token = self._jwt_service.generate_tokens(user_id, username)
        response.set_cookie("accessToken", access_token, httponly=True, secure=True, max_age=self._access_max_age)
        response.set_cookie("refreshToken", refresh_token, httponly=True, secure=True, max_age=self._refresh_max_age)

    async def create(self, username: str, password: str, response: Response) -> UserResponse:
        if await self._storage.retrieve_by_username(username):
            raise HTTPException(status_code=400, detail="User already exists")
        user = User(
            id=uuid4(),
            username=username,
            bio="",
            password_hash=hash_password(password),
        )
        await self._storage.save(user)
        self._set_auth_cookies(response, user.id, user.username)
        return UserResponse(
            username=user.username,
            bio=user.bio,
        )

    async def login(self, username: str, password: str, response: Response) -> UserResponse:
        user = await self._storage.retrieve_by_username(username)
        if user is None:
            raise HTTPException(status_code=403, detail=AUTH_ERROR_MSG)
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=403, detail=AUTH_ERROR_MSG)

        self._set_auth_cookies(response, user.id, user.username)
        return UserResponse(
            username=user.username,
            bio=user.bio,
        )

    async def refresh(self, refresh_token: str, response: Response) -> UserResponse:
        payload = self._jwt_service.verify_refresh_token(refresh_token)
        if payload is None:
            raise HTTPException(status_code=403, detail=AUTH_ERROR_MSG)
        user = await self._storage.retrieve(UUID(payload.sub))
        self._set_auth_cookies(response, user.id, user.username)
        return UserResponse(
            username=user.username,
            bio=user.bio,
        )

    @staticmethod
    def logout(response: Response) -> dict:
        response.set_cookie("accessToken", "", httponly=True, secure=True, max_age=0)
        response.set_cookie("refreshToken", "", httponly=True, secure=True, max_age=0)
        return {}

    async def profile(self, user_id: str) -> UserResponse:
        user = await self._storage.retrieve(UUID(user_id))
        return UserResponse(
            username=user.username,
            bio=user.bio,
        )

    async def update_bio(self, user_id: str, bio: str) -> UserResponse:
        user = await self._storage.update_bio(UUID(user_id), bio)
        return UserResponse(
            username=user.username,
            bio=user.bio,
        )


def get_user_resource(
    storage: IUserRepository = Depends(get_user_storage),
    jwt_service: JWTService = Depends(get_jwt_service),
    settings: Settings = Depends(get_settings),
) -> UserResource:
    return UserResource(
        storage=storage,
        jwt_service=jwt_service,
        access_max_age=settings.jwt_access_max_age,
        refresh_max_age=settings.jwt_refresh_max_age,
    )
