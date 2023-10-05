from fastapi import APIRouter
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code

menu_router = APIRouter(prefix="/menu", tags=["Menu"])


@menu_router.get("")
async def get_menu():
    return "menu router hello world"
