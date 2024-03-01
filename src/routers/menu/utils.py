import io
import logging
from src.constants.logger import CONSOLE_LOGGER_NAME
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.constants.image import ALLOWED_EXTENSION_IMAGE
from src.schemas.order import (
    CreateMenuSchema,
    CreateOrderSchema,
    AddNewItemSchema,
    AddNewItemByOrderIDSchema
)

from src.models.order import Menu, Order
from src.core.templates.fastapi_minio import minio_client
from uuid import uuid4
import cloudinary
import cloudinary.uploader
from bson import ObjectId

cloudinary.config(
    cloud_name="dsij6mntp",
    api_key="189381149557242",
    api_secret="f1Wq2eqAXeZqmI9ubM9cAc989mo",
)
logger = logging.getLogger(CONSOLE_LOGGER_NAME)


async def upload_img_v1(img: UploadFile) -> str:
    if img:
        print(f"img.file: {img.file}")
        file_extension = img.filename.split(".")[-1]
        if file_extension not in ALLOWED_EXTENSION_IMAGE:
            raise ErrorResponseException(**get_error_code(4000102))
        upload_result = cloudinary.uploader.upload(img.file, folder="scc-doi")
        print("pass step upload")
        if not upload_result:
            raise ErrorResponseException(**get_error_code(5000101))
        print(f"upload_result: {upload_result}")
    return upload_result


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
    img_url = await upload_img(image)
    new_menu = Menu(
        title=request_data.title.lower(), link=request_data.link, image_name=img_url
    )
    try:
        exist_menu = await Menu.find_one({"title":request_data.title.lower()})
        if exist_menu:
            raise ValueError("menu already exist")
        await new_menu.insert()
    except Exception as e:
        logger.error(f"Error when create new menu: {e}")
        raise ErrorResponseException(**get_error_code(4000105))

    return new_menu.model_dump()


async def create_new_order(request_data: CreateOrderSchema, current_user: str):
    current_menu = await Menu.find_one({"title": request_data.menu})
    if not current_menu:
        raise ErrorResponseException(**get_error_code(4000107))

    item_list_as_dict = [item.model_dump() for item in request_data.item_list]

    new_order = Order(
        created_by=current_user,
        title=request_data.title,
        description=request_data.description,
        namesAllowed=request_data.namesAllowed,
        menu=request_data.menu,
        area=request_data.area,
        share=request_data.share,
        order_date=request_data.order_date,
        item_list=item_list_as_dict,
        tags=request_data.tags,
    )

    try:
        await new_order.insert()
    except Exception as e:
        logger.error(f"Error when create order: {e}")
        raise ErrorResponseException(**get_error_code(4000109))

    return new_order.model_dump()


async def get_order():
    result = Order.find_all()

    return_data = []
    async for data in result:
        return_data.append(data.model_dump())
    return return_data


async def get_menu():
    result = Menu.find_all()

    return_data = []
    async for data in result:
        return_data.append(data.model_dump())
    return return_data


async def get_image_of_menu(request_data: str):
    if not request_data:
        file_object = io.open("src/data/default_logo.png", "rb", 0)
        file_extension = "png"
        return StreamingResponse(
            file_object,
            headers={
                "Content-Disposition": "inline",
                "Content-type": f"image/{file_extension}",
                "Cache-Control": "max-age=290304000, public",
            },
        )
    file_extension = request_data.split(".")[-1]
    if file_extension not in ALLOWED_EXTENSION_IMAGE:
        raise ErrorResponseException(**get_error_code(4000102))
    minio_url = await minio_client.get_url(f"/menu/{request_data}")
    if not minio_url:
        raise ErrorResponseException(**get_error_code(5000102))
    return minio_url


async def add_new_item_to_order(request_data: AddNewItemSchema):
    current_order = await Order.find_one(
        {
            "title": request_data.order.title,
            "description": request_data.order.description,
            "namesAllowed": request_data.order.namesAllowed,
            "menu": request_data.order.menu,
            "area": request_data.order.area,
            "share": request_data.order.share,
            "tags": request_data.order.tags,
            "owner": request_data.order.owner,
        }
    )

    if not current_order:
        raise ErrorResponseException(**get_error_code(4000111))

    current_item_list = current_order.item_list

    for item in request_data.new_item:
        current_item_list.append(item.model_dump())

    current_order.update({"$set": {"item_list": current_item_list}})

    return current_order.model_dump()


async def add_new_item_to_order_by_id(request_data: AddNewItemByOrderIDSchema):
    current_order = await Order.find_one(
        {
            "_id" : ObjectId(request_data.order_id)
        }

    )

    if not current_order:
        raise ErrorResponseException(**get_error_code(4000111))
    
    current_item_list = current_order.item_list
    for item in request_data.new_item:
        current_item_list.append(item.model_dump())

    # current_order.update({"$set": {"item_list": current_item_list}})
    await current_order.set({"item_list": current_item_list})
    await current_order.save()

    return current_order.model_dump()