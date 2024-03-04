import time

import jwt
from src.settings.auth_settings import auth_settings
from passlib.context import CryptContext

JWT_SECRET = auth_settings.SECRET
JWT_ALGORITHM = auth_settings.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_pwd, hashed_pwd) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_password_hash(pwd):
    return pwd_context.hash(pwd)


def authenticate_user(user_in_db: dict, password: str) -> bool:
    if not user_in_db:
        return False
    if not verify_password(password, user_in_db["password"]):
        return False
    return True


def create_access_token(data: dict, expires_delta: float | None = None):
    to_encode = {"fullname": data["fullname"], "username": data["username"], "is_refresh_token" : False}
    to_encode_2 = {"fullname": data["fullname"], "username": data["username"], "is_refresh_token" : True}
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + 600
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)
    expire = expire + 60000
    to_encode.update({"exp": expire})
    encoded_token_2 = jwt.encode(to_encode_2, JWT_SECRET, JWT_ALGORITHM)
    return {
        "access_token": encoded_token,
        "refresh_token" : encoded_token_2,
        "token_type": "bearer",
        "fullname": data["fullname"],
        "username": data["username"],
    }

def do_refresh_token(token : str | None = None):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    if payload['is_refresh_token'] is True:

        payload['exp'] = time.time() + 600
        payload['is_refresh_token'] = False

        encoded_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

        return {
        "access_token": encoded_token,
        "token_type": "bearer",
        "fullname": payload["fullname"],
        "username": payload["username"],
        }
    else:
        raise ValueError("refresh_token invalid !")