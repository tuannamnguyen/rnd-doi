def get_error_code(error_code: int, data: str = None):
    if data:
        message_error = ERROR_CODE.get(error_code, "Error code is not defined").replace(
            "{values}", str(data)
        )
    else:
        message_error = ERROR_CODE.get(error_code, "Error code is not defined")
    return {
        "success": False,
        "error_code": error_code,
        "error": message_error,
        "data": [],
    }


ERROR_CODE = {4000101: "test error code"}
