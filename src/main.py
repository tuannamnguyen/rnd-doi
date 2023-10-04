from fastapi import FastAPI
import json
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from src.exception.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(ErrorResponseException)
async def error_response_handler(request: Request, exception: ErrorResponseException):
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


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exception: RequestValidationError
):
    details = json.loads(exception.json())[0]
    err_msg = f"{details.get('loc')[-1]} - {details.get('msg')}"
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


@app.get("/")
async def root():
    return {"message": "Hello World"}
