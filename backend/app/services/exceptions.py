"""统一异常体系 - 符合 docs/09_Service设计.md 第18节"""


class ServiceError(Exception):
    """服务层异常基类"""
    pass


class NotFoundError(ServiceError):
    """资源不存在"""
    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource}不存在: {resource_id}")


class ValidationError(ServiceError):
    """数据验证失败"""
    pass


class ConflictError(ServiceError):
    """数据冲突"""
    pass


class WorkflowError(ServiceError):
    """工作流执行错误"""
    pass


class MemoryError(ServiceError):
    """记忆系统错误"""
    pass


class ToolExecutionError(ServiceError):
    """工具执行错误"""
    pass


class LLMError(ServiceError):
    """LLM调用错误"""
    pass
