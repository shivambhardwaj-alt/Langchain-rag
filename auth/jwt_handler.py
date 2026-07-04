import jwt 
import datetime
import os
from dotenv import load_dotenv
load_dotenv()


SECRET = os.getenv("SECRET_KEY")


def  create_token(user_id: str): 
    payload  =  { 
                 "user_id" : user_id ,
                 "exp"  : datetime.datetime.utcnow() + datetime.timedelta(hours= 2)                 
                 }
    return jwt.encode(payload, SECRET , algorithm = 'HS256')


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("Token expired")
    except jwt.InvalidTokenError:
        print("Invalid token")
    return None
