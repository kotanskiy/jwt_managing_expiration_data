from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from infrastructure.auth.jwt import Payload
from app.user.resource import UserResponse, UserResource
from infrastructure.auth.dependencies import jwt_auth
from infrastructure.user.dependencies import get_user_resource

router = APIRouter()


class UpdateUserSchema(BaseModel):
    bio: str = Field(..., title="Bio", description="Description about user", max_length=255)


@router.get(
    "/profile/",
    response_model=UserResponse,
    tags=["user"],
    name="Get user profile",
)
async def profile(
    resource: UserResource = Depends(get_user_resource),
    jwt: Payload = Depends(jwt_auth),
):
    return await resource.retrieve(UUID(jwt.sub))


@router.put(
    "/profile/",
    response_model={},
    tags=["user"],
    name="Updated user profile"
)
async def update_profile(
    data: UpdateUserSchema,
    jwt: Payload = Depends(jwt_auth),
    resource: UserResource = Depends(get_user_resource),
):
    return await resource.update(UUID(jwt.sub), data.bio)
