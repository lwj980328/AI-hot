"""ToolRegistry 单元测试

测试工具注册、发现、重复注册等功能。
"""

import pytest
from pydantic import BaseModel

from app.tools.base import BaseTool, ToolRegistry
from app.tools.base.exceptions import ToolNotFoundError


class DummyInput(BaseModel):
    keyword: str


class DummyOutput(BaseModel):
    result: str


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "Dummy tool for testing"
    version = "0.1.0"
    input_schema = DummyInput
    output_schema = DummyOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        return DummyOutput(result="ok")


@pytest.fixture
def registry():
    """创建一个新的 ToolRegistry 实例用于测试"""
    # 重置单例
    ToolRegistry._instance = None
    reg = ToolRegistry()
    yield reg
    ToolRegistry._instance = None


def test_register_and_get(registry):
    """测试工具注册和获取"""
    tool = DummyTool()
    registry.register(tool)

    retrieved = registry.get_tool("dummy_tool")
    assert retrieved is tool
    assert retrieved.name == "dummy_tool"


def test_get_not_found(registry):
    """测试获取未注册的工具抛出异常"""
    with pytest.raises(ToolNotFoundError):
        registry.get_tool("nonexistent_tool")


def test_list_tools(registry):
    """测试列出所有工具"""
    registry.register(DummyTool())
    tools = registry.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "dummy_tool"


def test_has_tool(registry):
    """测试检查工具是否存在"""
    assert not registry.has_tool("dummy_tool")
    registry.register(DummyTool())
    assert registry.has_tool("dummy_tool")


def test_override_register(registry):
    """测试重复注册覆盖旧工具"""
    tool1 = DummyTool()
    tool2 = DummyTool()
    tool2.version = "0.2.0"

    registry.register(tool1)
    registry.register(tool2)

    retrieved = registry.get_tool("dummy_tool")
    assert retrieved.version == "0.2.0"
