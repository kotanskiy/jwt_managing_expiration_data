from fastapi import FastAPI

from app.auth import views as auth_views
from app.user import views as user_views

app = FastAPI()

app.include_router(prefix="/auth", router=auth_views.router)
app.include_router(prefix="/user", router=user_views.router)


@app.get("/")
async def root():
    return {
        "info": "Experimental Api for manage expiration time from server"
    }
