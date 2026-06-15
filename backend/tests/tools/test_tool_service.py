"""ToolService 单元测试

测试重试机制、异常转换、输入/输出校验。
"""

import pytest
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel

from app.tools.base import BaseTool, ToolRegistry, ToolService
from app.tools.base.exceptions import (
    ToolError,
    ToolTimeoutError,
    ToolConnectionError,
    ToolNotFoundError,
    ToolValidationError,
)


class DummyInput(BaseModel):
    keyword: str


class DummyOutput(BaseModel):
    result: str


class SuccessTool(BaseTool):
    name = "success_tool"
    description = "Always succeeds"
    version = "0.1.0"
    input_schema = DummyInput
    output_schema = DummyOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        return DummyOutput(result="success")


class FailTool(BaseTool):
    name = "fail_tool"
    description = "Always fails with ToolError"
    version = "0.1.0"
    input_schema = DummyInput
    output_schema = DummyOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        raise ToolConnectionError("connection failed")


class RetryThenSuccessTool(BaseTool):
    name = "retry_tool"
    description = "Fails twice then succeeds"
    version = "0.1.0"
    input_schema = DummyInput
    output_schema = DummyOutput

    def __init__(self):
        self.attempt_count = 0

    async def execute(self, input_data: BaseModel) -> BaseModel:
        self.attempt_count += 1
        if self.attempt_count < 3:
            raise ToolTimeoutError("timeout")
        return DummyOutput(result="finally succeeded")


@pytest.fixture
def setup_services():
    """设置 ToolRegistry 和 ToolService 单例"""
    ToolRegistry._instance = None
    ToolService._instance = None

    registry = ToolRegistry()
    service = ToolService()

    yield registry, service

    ToolRegistry._instance = None
    ToolService._instance = None


@pytest.mark.asyncio
async def test_execute_success(setup_services):
    """测试工具执行成功"""
    registry, service = setup_services
    registry.register(SuccessTool())

    result = await service.execute("success_tool", DummyInput(keyword="test"))

    assert isinstance(result, DummyOutput)
    assert result.result == "success"


@pytest.mark.asyncio
async def test_execute_tool_not_found(setup_services):
    """测试工具未注册时抛出异常"""
    _, service = setup_services

    with pytest.raises(ToolNotFoundError):
        await service.execute("nonexistent", DummyInput(keyword="test"))


@pytest.mark.asyncio
async def test_execute_retry_then_success(setup_services):
    """测试重试机制：前两次失败，第三次成功"""
    registry, service = setup_services
    tool = RetryThenSuccessTool()
    registry.register(tool)

    result = await service.execute("retry_tool", DummyInput(keyword="test"))

    assert isinstance(result, DummyOutput)
    assert result.result == "finally succeeded"
    assert tool.attempt_count == 3


@pytest.mark.asyncio
async def test_execute_retry_exhausted(setup_services):
    """测试重试次数耗尽后抛出最后的异常"""
    registry, service = setup_services
    registry.register(FailTool())

    with pytest.raises(ToolConnectionError):
        await service.execute("fail_tool", DummyInput(keyword="test"))


@pytest.mark.asyncio
async def test_execute_input_type_mismatch(setup_services):
    """测试输入类型不匹配时抛出验证异常"""
    registry, service = setup_services
    registry.register(SuccessTool())

    # 传入错误的输入类型
    class WrongInput(BaseModel):
        wrong_field: str

    with pytest.raises(ToolValidationError):
        await service.execute("success_tool", WrongInput(wrong_field="test"))


@pytest.mark.asyncio
async def test_list_available_tools(setup_services):
    """测试列出所有可用工具"""
    registry, service = setup_services
    registry.register(SuccessTool())

    tools = service.list_available_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "success_tool"
