from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应结构

    遵循 docs/08_API设计.md 第 4 节规范：
    {
        "success": true,
        "message": "ok",
        "data": {}
    }
    """

    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="ok", description="响应消息")
    data: T | None = Field(default=None, description="响应数据")

    @classmethod
    def ok(cls, data: T, message: str = "ok") -> "ApiResponse[T]":
        """成功响应"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message: str, data: T | None = None) -> "ApiResponse[T]":
        """错误响应"""
        return cls(success=False, message=message, data=data)


class PaginatedData(BaseModel, Generic[T]):
    """分页数据"""

    items: list[T] = Field(description="数据列表")
    total: int = Field(description="总数")
    limit: int = Field(description="每页数量")
    offset: int = Field(description="偏移量")
