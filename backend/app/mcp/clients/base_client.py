"""MCP Client 抽象基类

对应 docs/06_MCP设计规范.md 第9节。
所有 MCP Client 实现必须继承此类。
"""

from abc import ABC, abstractmethod
from typing import Any

from app.mcp.schemas.metadata import MCPToolMetadata


class BaseMCPClient(ABC):
    """MCP Client 抽象基类

    定义与 MCP Server 通信的统一接口。
    """

    def __init__(self, server_id: str):
        self._server_id = server_id
        self._connected = False

    @property
    def server_id(self) -> str:
        """获取 Server ID"""
        return self._server_id

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """建立与 MCP Server 的连接"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开与 MCP Server 的连接"""
        pass

    @abstractmethod
    async def list_tools(self) -> list[MCPToolMetadata]:
        """获取 MCP Server 暴露的所有工具

        Returns:
            工具元数据列表
        """
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """调用 MCP Server 上的工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        pass
