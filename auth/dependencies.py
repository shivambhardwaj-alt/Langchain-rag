from fastapi import Header , HTTPException 
from auth.jwt_handler import verify_token


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user