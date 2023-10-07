import json

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.constants.error_code import get_error_code
from src.exceptions.error_response_exception import ErrorResponseException


def error_response_handler(request: Request, exception: ErrorResponseException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "success": exception.success,
            "data": exception.data,
            "length_data": exception.length_data,
            "error": exception.error,
            "error_code": exception.error_code,
        },
    )


def request_validation_error_handler(
    request: Request, exception: RequestValidationError
):
    err_msg = jsonable_encoder({"detail": exception.errors()})
    return JSONResponse(
        status_code=200,
        content={
            "error": err_msg,
            "success": False,
            "data": None,
            "status_code": 200,
            "error_code": 4000100,
            "length_data": 0,
        },
    )
