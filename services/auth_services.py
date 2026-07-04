from auth.jwt_handler import create_token
import bcrypt

fake_users_db = {}  # replace this thing with the real database and not supposed to use dictionary here

def register_user(payload):
    user_id = str(len(fake_users_db) + 1)

    hashed_password = bcrypt.hashpw(
        payload.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    fake_users_db[user_id] = {
        "email": payload.email,
        "password": hashed_password,
    }

    token = create_token(user_id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def login_user(payload):
    for user_id, user in fake_users_db.items():

        if user["email"] == payload.email:

            if bcrypt.checkpw(
                payload.password.encode("utf-8"),
                user["password"].encode("utf-8")
            ):
                return {
                    "access_token": create_token(user_id),
                    "token_type": "bearer"
                }

            return {"error": "Invalid credentials"}

    return {"error": "Invalid credentials"}
 
    