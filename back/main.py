from fastapi import FastAPI, Depends, Response
from pydantic import BaseModel, Field

from user.resource import UserResponse, UserResource, get_user_resource
from auth import jwt_auth

app = FastAPI()


class Credentials(BaseModel):
    username: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


class UpdateUserSchema(BaseModel):
    bio: str = Field(..., title="Bio", description="Description about user", max_length=255)


@app.post(
    "/user/registration/",
    response_model=UserResponse,
    tags=["auth"],
    name="Registration user",
    description="Registration user and login with jwt token"
)
async def registration(
    data: Credentials,
    response: Response,
    resource: UserResource = Depends(get_user_resource),
):
    return await resource.create(
        username=data.username,
        password=data.password,
        response=response,
    )


@app.post(
    "/user/login/",
    response_model=UserResponse,
    tags=["auth"],
    name="Login user",
    description="Login with "
)
async def login(
    data: Credentials,
    response: Response,
    resource: UserResource = Depends(get_user_resource),
):
    return await resource.login(data.username, data.password, response)


@app.post(
    "/user/refresh_token/",
    response_model=UserResponse,
    tags=["auth"],
    name="Refresh jwt token",
)
async def refresh_token(
    data: RefreshToken,
    response: Response,
    resource: UserResource = Depends(get_user_resource),
):
    return await resource.refresh(data.refresh_token, response)


@app.post(
    "/user/logout/",
    response_model={},
    tags=["auth"],
    name="Logout user",
)
async def logout(
    response: Response,
    resource: UserResource = Depends(get_user_resource),
    _: str = Depends(jwt_auth),
):
    return resource.logout(response)


@app.get(
    "/user/profile/",
    response_model=UserResponse,
    tags=["user"],
    name="Get user profile",
)
async def profile(
    resource: UserResource = Depends(get_user_resource),
    user_id: str = Depends(jwt_auth),
):
    return await resource.profile(user_id)


@app.put(
    "/user/profile/",
    response_model=UserResponse,
    tags=["user"],
    name="Updated user profile"
)
async def update_profile(
    data: UpdateUserSchema,
    user_id: str = Depends(jwt_auth),
    resource: UserResource = Depends(get_user_resource),
):
    return await resource.update_bio(user_id, data.bio)


@app.get("/")
async def root():
    return {
        "info": "Experimental Api for manage expiration time from server"
    }
