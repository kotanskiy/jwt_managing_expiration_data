from functools import wraps, partial
from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from infrastructure.auth.jwt import JWTService, Payload
from infrastructure.auth.permissions import Permissions
from infrastructure.user.dependencies import get_user_service
from app.auth.resource import AuthResource, AUTH_ERROR_MSG
from conf import Settings, get_settings
from domain.services import UserService



def get_jwt_service(settings: Settings = Depends(get_settings)) -> JWTService:
    return JWTService(
        access_secret=settings.jwt_access_secret,
        refresh_secret=settings.jwt_refresh_secret,
        access_max_age=settings.jwt_access_max_age,
        refresh_max_age=settings.jwt_refresh_max_age,
    )


def get_auth_resource(
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings),
) -> AuthResource:
    return AuthResource(
        jwt_service=jwt_service,
        user_service=user_service,
        settings=settings,
    )


def jwt_auth(
    jwt_service: JWTService = Depends(get_jwt_service),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> Payload:
    token: str = credentials.credentials
    try:
        return jwt_service.verify_access_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail=AUTH_ERROR_MSG)


def has_permission(*permissions: Permissions, payload: Payload = Depends(jwt_auth)):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            print(payload)
            for p in permissions: # type: Permissions
                p.verify_permission(payload.permissions)
            return func(*args, **kwargs)
        return inner
    return wrapper

