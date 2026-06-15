"""STDIO MCP Client 实现

基于 mcp 官方 Python SDK 实现本地进程模式的 MCP 通信。
对应 docs/06_MCP设计规范.md 第10节。
"""

import logging
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.mcp.clients.base_client import BaseMCPClient
from app.mcp.schemas.config import MCPServerConfig
from app.mcp.schemas.metadata import MCPToolMetadata

logger = logging.getLogger(__name__)


class STDIOMCPClient(BaseMCPClient):
    """STDIO 模式的 MCP Client

    通过标准输入/输出与本地 MCP Server 进程通信。
    """

    def __init__(self, config: MCPServerConfig):
        super().__init__(config.server_id)
        self._config = config
        self._session: ClientSession | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def connect(self) -> None:
        """启动 MCP Server 子进程并建立连接"""
        if self._connected:
            logger.warning(f"MCP Client '{self._server_id}' 已连接，跳过")
            return

        if not self._config.command:
            raise ValueError(f"MCP Server '{self._server_id}' 缺少 command 配置")

        try:
            self._exit_stack = AsyncExitStack()

            # 构建服务器参数
            server_params = StdioServerParameters(
                command=self._config.command,
                args=self._config.args or [],
                env=self._config.env if self._config.env else None,
            )

            # 建立 STDIO 连接
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport

            # 创建会话
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # 初始化会话
            await self._session.initialize()

            self._connected = True
            logger.info(f"MCP Client '{self._server_id}' 已连接")

        except Exception as e:
            logger.error(f"MCP Client '{self._server_id}' 连接失败: {e}")
            await self._cleanup()
            raise

    async def disconnect(self) -> None:
        """断开连接并清理子进程"""
        if not self._connected:
            return

        await self._cleanup()
        logger.info(f"MCP Client '{self._server_id}' 已断开")

    async def _cleanup(self) -> None:
        """清理资源"""
        self._connected = False
        self._session = None
        if self._exit_stack:
            try:
                await self._exit_stack.aclose()
            except Exception as e:
                logger.warning(f"MCP Client '{self._server_id}' 清理资源时出错: {e}")
            finally:
                self._exit_stack = None

    async def list_tools(self) -> list[MCPToolMetadata]:
        """获取 MCP Server 暴露的所有工具"""
        if not self._connected or not self._session:
            raise RuntimeError(f"MCP Client '{self._server_id}' 未连接")

        try:
            result = await self._session.list_tools()
            tools = []
            for tool in result.tools:
                metadata = MCPToolMetadata(
                    tool_name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema if tool.inputSchema else {},
                    output_schema=tool.outputSchema if hasattr(tool, "outputSchema") and tool.outputSchema else {},
                    server_id=self._server_id,
                )
                tools.append(metadata)
            return tools

        except Exception as e:
            logger.error(f"MCP Client '{self._server_id}' 获取工具列表失败: {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """调用 MCP Server 上的工具"""
        if not self._connected or not self._session:
            raise RuntimeError(f"MCP Client '{self._server_id}' 未连接")

        try:
            logger.info(f"调用 MCP 工具: {tool_name}, 参数: {arguments}")
            result = await self._session.call_tool(tool_name, arguments)

            # 提取结果内容
            if result.content:
                # 合并所有 content 的文本
                texts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        texts.append(content.text)
                return "\n".join(texts) if texts else str(result.content)
            return None

        except Exception as e:
            logger.error(f"MCP 工具 '{tool_name}' 调用失败: {e}")
            raise
