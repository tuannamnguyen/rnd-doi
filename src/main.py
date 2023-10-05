from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.exceptions.error_response_exception import ErrorResponseException
from src.exceptions.exception_handler import (
    error_response_handler,
    request_validation_error_handler,
)
from src.routers.menu.views import menu_router

app = FastAPI()

app.add_exception_handler(ErrorResponseException, error_response_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

app.include_router(menu_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
