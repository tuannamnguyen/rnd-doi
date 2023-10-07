from fastapi import APIRouter, UploadFile, Depends, File
from src.schemas.response import ApiResponse
from src.schemas.order import CreateMenuSchema, CreateItemSchema, CreateOrderSchema
from src.routers.menu.utils import create_new_menu, create_new_item, create_new_order

menu_router = APIRouter(prefix="/api/menu", tags=["Menu"])


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


@menu_router.post("/create_item", response_model=ApiResponse)
async def create_item(request_data: CreateItemSchema):
    result = await create_new_item(request_data)
    return {"data": [result]}


@menu_router.post("/create_order", response_model=ApiResponse)
async def create_order(request_data: CreateOrderSchema):
    result = await create_new_order(request_data)
    return {"data": [result]}
