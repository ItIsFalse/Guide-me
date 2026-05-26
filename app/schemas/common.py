from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")


class BaseResponse(BaseModel):
    success: bool = True
    message: str = "OK"


class DataResponse(BaseResponse, Generic[T]):
    data: T | None = None


class PaginatedResponse(BaseResponse, Generic[T]):
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: str | None = None