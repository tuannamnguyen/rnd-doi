from typing import Any, List


class ErrorResponseException(Exception):
    def __init__(
        self,
        error: str,
        success: bool = False,
        data: List[Any] = [],
        status_code: int = 200,
        error_code: int = 0,
    ):
        self.error = error
        self.success = success
        self.data = data
        self.status_code = status_code
        self.error_code = error_code
        self.length_data = len(data) if data else 0

    def dict(self):
        return {
            "error": self.error,
            "success": self.success,
            "data": self.data,
            "status_code": self.status_code,
            "error_code": self.error_code,
            "length_data": self.length_data,
        }
