import io
import logging
from src.constants.logger import CONSOLE_LOGGER_NAME
from fastapi import UploadFile
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.constants.image import ALLOWED_EXTENSION_IMAGE
from src.schemas.order import CreateMenuSchema, CreateOrderSchema
from src.models.order import Menu, Order
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
        title=request_data.title, link=request_data.link, image_name=img_name
    )
    try:
        await new_menu.commit()
    except Exception as e:
        logger.error(f"Error when create new menu: {e}")
        raise ErrorResponseException(**get_error_code(4000105))

    return new_menu.dump()


async def create_new_order(request_data: CreateOrderSchema):
    new_order = Order(
        title=request_data.title,
        description=request_data.description,
        menu=request_data.menu,
        area=request_data.area,
        share=request_data.share,
        time_order=request_data.time_order,
        participants=request_data.participants,
        item=request_data.item,
    )
    try:
        await new_order.commit()
    except Exception as e:
        logger.error(f"Error when create new order: {e}")
        raise ErrorResponseException(**get_error_code(4000106))

    return new_order.dump()
