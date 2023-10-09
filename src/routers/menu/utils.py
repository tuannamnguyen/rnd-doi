import io
import logging
from src.constants.logger import CONSOLE_LOGGER_NAME
from fastapi import UploadFile
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.constants.image import ALLOWED_EXTENSION_IMAGE
from src.schemas.order import CreateMenuSchema, CreateItemSchema, CreateOrderSchema
from src.models.order import Menu, Item, Order
from src.core.templates.fastapi_minio import minio_client
from uuid import uuid4

logger = logging.getLogger(CONSOLE_LOGGER_NAME)


async def upload_img(img: UploadFile) -> str:
    file_name = ""
    if img:
        file_extension = img.filename.split(".")[-1]
        if file_extension not in ALLOWED_EXTENSION_IMAGE:
            raise ErrorResponseException(**get_error_code(4000102))
        file_name = str(uuid4()) + "." + file_extension
        upload_file = io.BytesIO(await img.read())
        upload_response = await minio_client.put_object(
            f"/menu/{file_name}", data=upload_file
        )
        if not upload_response:
            raise ErrorResponseException(**get_error_code(5000101))
    return file_name


async def create_new_menu(request_data: CreateMenuSchema, image: UploadFile):
    img_name = await upload_img(image)
    new_menu = Menu(
        title=request_data.title.lower(), link=request_data.link, image_name=img_name
    )
    try:
        await new_menu.commit()
    except Exception as e:
        logger.error(f"Error when create new menu: {e}")
        raise ErrorResponseException(**get_error_code(4000105))

    return new_menu.dump()


async def create_new_item(request_data: CreateItemSchema):
    if not (await Menu.find_one({"title": request_data.menu})):
        raise ErrorResponseException(**get_error_code(4000107))
    new_item = Item(
        menu=request_data.menu.lower(),
        name=request_data.name,
        food=request_data.food,
        price=request_data.price,
        quantity=request_data.quantity,
        total=request_data.quantity * request_data.price,
    )
    try:
        await new_item.commit()
    except Exception as e:
        logger.error(f"Error when create new item: {e}")
        raise ErrorResponseException(**get_error_code(4000108))

    return new_item.dump()


async def create_new_order(request_data: CreateOrderSchema):
    item_list = []
    for item in request_data.item_list:
        order_item = await Item.find_one(
            {
                "menu": item.menu,
                "name": item.name,
                "food": item.food,
                "price": item.price,
                "quantity": item.quantity,
                "total": item.price * item.quantity,
            }
        )
        if not order_item:
            raise ErrorResponseException(**get_error_code(4000110))
        item_list.append(order_item)

    new_order = Order(
        title=request_data.title,
        description=request_data.description,
        menu=request_data.menu,
        area=request_data.area,
        share=request_data.share,
        order_date=request_data.order_date,
        item_list=item_list,
    )

    try:
        await new_order.commit()
    except Exception as e:
        logger.error(f"Error when create order: {e}")
        raise ErrorResponseException(**get_error_code(4000109))

    return new_order.dump()


async def get_order():
    result = Order.find({})

    return_data = []
    async for data in result:
        return_data.append(data.dump())
    return return_data


async def get_menu():
    result = Menu.find({})

    return_data = []
    async for data in result:
        return_data.append(data.dump())
    return return_data


async def get_item():
    result = Item.find({})

    return_data = []
    async for data in result:
        return_data.append(data.dump())
    return return_data
