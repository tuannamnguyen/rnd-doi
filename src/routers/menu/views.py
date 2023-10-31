from fastapi import APIRouter, UploadFile, Depends, File, status
from src.schemas.response import ApiResponse
from src.schemas.order import (
    CreateMenuSchema,
    CreateOrderSchema,
    GetMenuImageSchema,
    AddNewItemSchema,
)
from src.routers.menu.utils import (
    create_new_menu,
    create_new_order,
    get_order,
    get_menu,
    get_image_of_menu,
    add_new_item_to_order,
)

from src.auth.auth_bearer import jwt_validator
from src.models.order import Menu, Order

menu_router = APIRouter(prefix="/api/menu", tags=["Menu"])


@menu_router.post(
    "/up_image", response_model=ApiResponse
)
async def up_image(image: UploadFile = File(...)):
    from src.routers.menu.utils import upload_img_v1
    result = await upload_img_v1(image)
    return {"data": []}

@menu_router.post(
    "/create_menu", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def create_menu(
    request_data: CreateMenuSchema = Depends(CreateMenuSchema.as_form),
    image: UploadFile = File(...),
):
    result = await create_new_menu(request_data, image)
    return {"data": [result]}


@menu_router.post(
    "/create_order", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def create_order(request_data: CreateOrderSchema):
    result = await create_new_order(request_data)
    return {"data": [result]}


@menu_router.post(
    "/get_all_order", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_all_order():
    result = await get_order()
    return {"data": result}


@menu_router.post(
    "/get_all_menu", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_all_menu():
    result = await get_menu()
    return {"data": result}


@menu_router.post(
    "/get_menu_image", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_menu_image(request_data: GetMenuImageSchema):
    result = await get_image_of_menu(request_data.image_name)
    return {"data": [result]}


@menu_router.post(
    "/add_new_item", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def add_new_item(request_data: AddNewItemSchema):
    result = await add_new_item_to_order(request_data)
    return {"data": [result]}


@menu_router.delete(
    "/{title}", dependencies=[Depends(jwt_validator)], status_code=status.HTTP_200_OK
)
async def delete_menu_by_title(title: str) -> dict:
    menu = await Menu.find_one({"title": title})
    if menu is not None:
        await Menu.collection.delete_one({"title": title})
        return menu.dump()
    raise HTTPException(status_code=404, detail=f"Menu {title} not found")


@menu_router.delete(
    "/delete_order/{title}",
    dependencies=[Depends(jwt_validator)],
    status_code=status.HTTP_200_OK,
)
async def delete_order_by_title(title: str) -> dict:
    order = await Order.find_one({"title": title})
    if order is not None:
        await Order.collection.delete_one({"title": title})
        return order.dump()
    raise HTTPException(status_code=404, detail=f"Order {title} not found")
