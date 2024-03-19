from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from src.constants.error_code import get_error_code
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.logger import CONSOLE_LOGGER_NAME
from src.models.order import Menu
from src.schemas.response import ApiResponse
from src.auth.auth_bearer import jwt_validator, get_current_user
from src.auth.auth_handler import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    do_refresh_token,
)
from src.models.users import User
from src.schemas.users import UserSchema, UpdateUserSchema
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
        if user.password != user.confirm_password:
            raise ValidationError("password and confirmation does not match")
        
        if user.area != 1 and user.area != 2:
            raise ValidationError("area not exist !")
        new_user_model = User(
            fullname=user.fullname, username=user.username, password=user.password,
            role="user", area=user.area
        )
        # Insert hashed password into DB
        new_user_model.password = get_password_hash(user.password)
        await new_user_model.insert()
        return new_user_model.model_dump()
    except ValidationError as e:
        logger.error(f"Fail to create new user: {e}")
        raise ErrorResponseException(**get_error_code(4000112))
    except Exception as e:
        logger.error(f"Fail to create new user: {e}")
        raise ErrorResponseException(**get_error_code(4000112))


@user_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_in_db = await User.find_one(User.username == form_data.username)
    user_in_db = user_in_db.model_dump()
    if user_in_db:
        authenticated = authenticate_user(user_in_db, form_data.password)
        if not authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        expires = 1200
        return create_access_token(user_in_db, expires_delta=expires)
    return {"detail": "User not found"}

@user_router.post(
        "/refesh_token", status_code=status.HTTP_200_OK
)
async def refresh_token(token : str):
    try:
        return {"detail" : do_refresh_token(token)}
    except Exception as e:
        return {"detail" : "refresh token invalid!"}


@user_router.delete(
    "/{username}", dependencies=[Depends(jwt_validator)], status_code=status.HTTP_200_OK
)
async def delete_user_by_username(username: str) -> dict:
    user = await User.find_one({"username": username})
    if user is not None:
        await user.delete()
        return user.model_dump()
    raise HTTPException(status_code=404, detail=f"User {username} not found")


@user_router.post(
    "/get_all_user", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_all_user():
    result = User.find_all()

    return_data = []
    async for data in result:
        return_data.append(data.model_dump())

    return {"data": return_data}



@user_router.post(
    "/update_user",  dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)

async def update_user(info : UpdateUserSchema , current_user:str = Depends(get_current_user)):
    current_user_info = await User.find_one({"username" : current_user})
    await current_user_info.set({"fullname" : info.fullname,
                                 "area" : info.area})
    current_user_info.save()

    return {"data" : [{"username" : current_user_info.username,
                       "fullname": current_user_info.fullname, 
                       "area" :current_user_info.area}]}
