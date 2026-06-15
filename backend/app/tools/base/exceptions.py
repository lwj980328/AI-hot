"""工具异常体系

统一工具层异常，便于 ToolService 做异常转换和降级处理。
对应 docs/03_工具设计规范.md 第13节。
"""

from app.services.exceptions import ServiceError


class ToolError(ServiceError):
    """工具异常基类"""
    pass


class ToolTimeoutError(ToolError):
    """工具调用超时"""
    pass


class ToolConnectionError(ToolError):
    """工具连接失败（网络、DNS、HTTP 5xx 等）"""
    pass


class ToolValidationError(ToolError):
    """工具输入/输出验证失败"""
    pass


class ToolAuthenticationError(ToolError):
    """工具认证失败（API Token 缺失或无效）"""
    pass


class ToolRateLimitError(ToolError):
    """工具触发限流"""
    pass


class ToolNotFoundError(ToolError):
    """工具未在 Registry 中注册"""
    pass
