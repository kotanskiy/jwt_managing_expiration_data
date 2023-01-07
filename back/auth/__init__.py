from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt import JWTService, get_jwt_service


def jwt_auth(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> str:
    """
    :return: user_id
    """
    access_token = credentials.credentials
    payload = jwt_service.verify_access_token(access_token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return payload.sub
