from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    jwt_access_secret: str
    jwt_access_max_age: int
    jwt_refresh_secret: str
    jwt_refresh_max_age: int
    mongo_url: str

    class Config:
        env_file = "conf/.env"


@lru_cache
def get_settings():
    return Settings()
