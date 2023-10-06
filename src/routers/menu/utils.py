import io
from fastapi import UploadFile
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.constants.image import ALLOWED_EXTENSION_IMAGE
from src.schemas.order import CreateMenuSchema
from src.models.order import Menu
from src.core.templates.fastapi_minio import minio_client
from uuid import uuid4


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
    await new_menu.commit()
    return new_menu.dump()
