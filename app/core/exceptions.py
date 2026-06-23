from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
