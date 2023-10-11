from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from src.constants.error_code import get_error_code
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.logger import CONSOLE_LOGGER_NAME


from src.auth.auth_bearer import jwt_validator
from src.auth.auth_handler import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from src.models.users import User
from src.schemas.users import UserSchema
from marshmallow.exceptions import ValidationError

user_router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(CONSOLE_LOGGER_NAME)


@user_router.get(
    "", dependencies=[Depends(jwt_validator)], status_code=status.HTTP_200_OK
)
async def get_all_users():
    return [user.dump() async for user in User.find()]


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_signup(user: UserSchema):
    try:
        user = jsonable_encoder(user)
        new_user_model = User(**user)
        # Insert hashed password into DB
        new_user_model.password = get_password_hash(user["password"])
        await new_user_model.commit()
        return new_user_model.dump()
    except ValidationError as e:
        logger.error(f"Fail to create new user: {e}")
        raise ErrorResponseException(**get_error_code(4000112))
    except Exception:
        raise ErrorResponseException(**get_error_code(4000112))


@user_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_in_db = await User.find_one({"username": form_data.username})
    user_in_db = user_in_db.dump()
    if user_in_db:
        authenticated = authenticate_user(user_in_db, form_data.password)
        if not authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        expires = 600
        return create_access_token(user_in_db, expires_delta=expires)
    return {"detail": "User not found"}


@user_router.delete(
    "/{username}", dependencies=[Depends(jwt_validator)], status_code=status.HTTP_200_OK
)
async def delete_user_by_username(username: str) -> dict:
    user = await User.find_one({"username": username})
    if user is not None:
        await User.collection.delete_one({"username": username})
        return user.dump()
    raise HTTPException(status_code=404, detail=f"User {username} not found")
