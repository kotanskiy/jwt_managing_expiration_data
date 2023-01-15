from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel, Field

from app.auth.resource import AuthResource
from app.user.resource import UserResponse
from infrastructure.auth.dependencies import get_auth_resource, has_permission
from infrastructure.auth.permissions import Permissions

router = APIRouter()


class UserCredentialsReq(BaseModel):
    username: str = Field(..., regex=r"^[a-zA-Z0-9_]+$", min_length=3, max_length=10)
    password: str = Field(..., regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$", min_length=6, max_length=20)


class RefreshReq(BaseModel):
    refresh_token: str


class PermissionResponse(BaseModel):
    name: str


@router.post(
    "/login/",
    response_model=UserResponse,
    tags=["auth"],
)
async def login(
    credentials: UserCredentialsReq,
    response: Response,
    resource: AuthResource = Depends(get_auth_resource)
) -> UserResponse:
    return await resource.login(credentials.username, credentials.password, response)


@router.post(
    "/refresh/",
    response_model=UserResponse,
    tags=["auth"],
)
async def refresh(
    refresh_req: RefreshReq,
    response: Response,
    resource: AuthResource = Depends(get_auth_resource)
) -> UserResponse:
    return await resource.refresh(refresh_req.refresh_token, response)


@router.post(
    "/registration/",
    response_model=UserResponse,
    tags=["auth"],
)
async def registration(
    credentials: UserCredentialsReq,
    response: Response,
    resource: AuthResource = Depends(get_auth_resource),
) -> UserResponse:
    return await resource.registration(credentials.username, credentials.password, response)


@router.post(
    "/logout/",
    response_model={},
    tags=["auth"],
)
def logout(
    response: Response,
    resource: AuthResource = Depends(get_auth_resource),
) -> dict:
    return resource.logout(response)


@router.get(
    "/permissions/",
    response_model=list[PermissionResponse],
    tags=["auth"],
)
async def permissions_list():
    return [PermissionResponse(name=p) for p in Permissions.values()]
