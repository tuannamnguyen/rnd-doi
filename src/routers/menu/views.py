from typing import Annotated
from fastapi import APIRouter, UploadFile, Depends, File, status
from src.schemas.response import ApiResponse
from src.schemas.order import (
    CreateMenuSchema,
    CreateOrderSchema,
    GetMenuImageSchema,
    GetFoodImageSchema,
    AddNewItemSchema,
    AddNewItemByOrderIDSchema,
    
)
from src.schemas.food import food_schema, AddNewItemSchemaV3
from src.models.food import Food
from src.routers.menu.utils import (
    create_new_menu,
    create_new_order,
    get_order,
    get_order_v2,
    get_menu,
    get_image_of_menu,
    add_new_item_to_order,
    add_new_item_to_order_by_id,
    add_new_food,
    get_all_food,
    get_food_by_menu_title,
    add_new_item_v3,
    do_get_order_by_id,
    do_get_food_by_order_id
    # get_food_by_menu_from_order
)

from src.auth.auth_bearer import jwt_validator, get_current_user, get_current_area
from src.models.order import Menu, Order, Item

menu_router = APIRouter(prefix="/api/menu", tags=["Menu"])


@menu_router.post("/up_image", response_model=ApiResponse)
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
async def create_order(request_data: CreateOrderSchema, current_user:str = Depends(get_current_user)):
    result = await create_new_order(request_data, current_user)
    return {"data": [result]}


@menu_router.post(
    "/get_all_order", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_all_order():
    result = await get_order()
    return {"data": result}

#-------------------[new get order]------------
@menu_router.post(
    "/get_user_order", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_order_by_user(current_user:str = Depends(get_current_user), current_area: int = Depends(get_current_area)):
    result = await get_order_v2(current_user, current_area)
    return {"data": result}
#----------------------------------------------


#---------------------[get order user by id]------------------
@menu_router.get(
    "/get_user_order/{order_id}", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_order_by_id(order_id : str):
    result =  await do_get_order_by_id(order_id)
    return {"data" : [result]}
#-------------------------------------------------------------


#---------------------[get foods by order id]------------------
@menu_router.get(
    "/get_user_order/{order_id}/foods", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def get_order_by_id(order_id : str):
    result =  await do_get_food_by_order_id(order_id)
    return {"data" : result}
#-------------------------------------------------------------

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
    "/add_new_item_old_v2", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
)
async def add_new_item(request_data: AddNewItemByOrderIDSchema, current_user:str = Depends(get_current_user)):
    result = await add_new_item_to_order_by_id(request_data, current_user)
    return {"data": [result]}

@menu_router.post(
    "/add_new_item_old_v1", dependencies=[Depends(jwt_validator)], response_model=ApiResponse
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
        await menu.delete()
        return menu.model_dump()


@menu_router.delete(
    "/delete_order/{title}",
    dependencies=[Depends(jwt_validator)],
    status_code=status.HTTP_200_OK,
)
async def delete_order_by_title(title: str) -> dict:
    order = await Order.find_one({"title": title})
    if order is not None:
        await order.delete()
        return order.model_dump()

#-------------------------[NEW FOOD MENU UPDATE]-------------------
@menu_router.post(
    "/add_new_food",
    dependencies=[Depends(jwt_validator)],
    response_model=ApiResponse
)

async def add_food_by_menu(request_data: food_schema = Depends(food_schema.as_form)
                           , image: UploadFile = File(...),):
    result = await add_new_food(request_data, image)

    return {"data" : [result]}


@menu_router.post("/get_all_food", dependencies=[Depends(jwt_validator)])
async def get_food():
    result = await get_all_food()

    return {"data" : result}



@menu_router.post("/get_food_by_menu", dependencies=[Depends(jwt_validator)])
async def get_food(menu_title : str):
    result = await get_food_by_menu_title(menu_title)

    return {"data" : result}


@menu_router.post("/add_new_item", dependencies=[Depends(jwt_validator)], response_model=ApiResponse)
async def add_food(request_data : AddNewItemSchemaV3, current_user:str = Depends(get_current_user)):
    result = await add_new_item_v3(current_user, request_data)

    return {"data" : [result]}


@menu_router.post("/get_food_image", dependencies=[Depends(jwt_validator)], response_model=ApiResponse)
async def show_food_image(request_data : GetFoodImageSchema):
    result = await get_image_of_menu(request_data.image_url)
    return {"data": [result]}

#-------------------------------------------------------------------