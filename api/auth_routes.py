from fastapi import APIRouter
from schemas.auth_schema import UserRegister, UserLogin
from services.auth_services import register_user, login_user
router = APIRouter(prefix = "/auth" , tags = ['Auth'])


@router.post("/register")
def register(payload : UserRegister):
    return register_user(payload)



@router.post("/login")
def login(payload : UserLogin):
    return login_user(payload)


