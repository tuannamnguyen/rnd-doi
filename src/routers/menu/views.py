from fastapi import APIRouter, UploadFile, Depends, File
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.schemas.response import ApiResponse
from src.schemas.order import CreateMenuSchema
from src.routers.menu.utils import create_new_menu

menu_router = APIRouter(prefix="/menu", tags=["Menu"])


@menu_router.get("")
async def get_menu():
    return "menu router hello world"


@menu_router.post("/create_menu", response_model=ApiResponse)
async def create_menu(
    request_data: CreateMenuSchema = Depends(CreateMenuSchema.as_form),
    image: UploadFile = File(...),
):
    result = await create_new_menu(request_data, image)
    return {"data": [result]}
