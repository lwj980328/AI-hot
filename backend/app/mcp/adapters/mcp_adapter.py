"""MCP Adapter

核心适配层，负责将 MCP 工具转换为 BaseTool 并注册到 ToolRegistry。
对应 docs/06_MCP设计规范.md 第16节。
对应 docs/03_工具设计规范.md 第9节。
"""

import logging

from app.mcp.discovery.discovery_service import MCPDiscoveryService, get_mcp_discovery_service
from app.mcp.manager.client_manager import MCPClientManager, get_mcp_client_manager
from app.mcp.tools.mcp_tool import MCPTool
from app.tools.base.registry import ToolRegistry, get_tool_registry

logger = logging.getLogger(__name__)


class MCPAdapter:
    """MCP 适配器

    职责：
    1. 协调 DiscoveryService 发现 MCP 工具
    2. 将 MCP 工具转换为 MCPTool (BaseTool)
    3. 注册到 ToolRegistry
    """

    def __init__(
        self,
        client_manager: MCPClientManager | None = None,
        discovery_service: MCPDiscoveryService | None = None,
        registry: ToolRegistry | None = None,
    ):
        self._client_manager = client_manager or get_mcp_client_manager()
        self._discovery_service = discovery_service or get_mcp_discovery_service()
        self._registry = registry or get_tool_registry()

    async def init_and_register(self, config_path: str | None = None) -> int:
        """初始化 MCP 并注册所有工具

        Args:
            config_path: MCP 配置文件路径

        Returns:
            成功注册的工具数量
        """
        # 1. 加载配置并初始化 Client
        await self._discovery_service.init_from_config(config_path)

        # 2. 发现所有 MCP 工具
        all_tools = await self._discovery_service.discover_all()

        # 3. 转换为 MCPTool 并注册
        registered_count = 0
        for server_id, tools_metadata in all_tools.items():
            client = self._client_manager.get_client(server_id)
            if not client:
                logger.error(f"MCP Client '{server_id}' 不存在，跳过工具注册")
                continue

            server_config = self._client_manager.get_config(server_id)

            for metadata in tools_metadata:
                try:
                    mcp_tool = MCPTool(
                        metadata=metadata,
                        client=client,
                        server_config=server_config,
                    )
                    self._registry.register(mcp_tool)
                    registered_count += 1
                    logger.info(f"注册 MCP 工具: {mcp_tool.name}")
                except Exception as e:
                    logger.error(f"注册 MCP 工具 '{metadata.tool_name}' 失败: {e}")

        logger.info(f"MCP 工具注册完成，共注册 {registered_count} 个工具")
        return registered_count

    async def register_server_tools(self, server_id: str) -> int:
        """注册指定 MCP Server 的所有工具

        Args:
            server_id: MCP Server ID

        Returns:
            成功注册的工具数量
        """
        # 发现该 Server 的工具
        tools_metadata = await self._discovery_service.discover(server_id)

        client = self._client_manager.get_client(server_id)
        if not client:
            logger.error(f"MCP Client '{server_id}' 不存在")
            return 0

        registered_count = 0
        for metadata in tools_metadata:
            try:
                mcp_tool = MCPTool(metadata=metadata, client=client)
                self._registry.register(mcp_tool)
                registered_count += 1
            except Exception as e:
                logger.error(f"注册 MCP 工具 '{metadata.tool_name}' 失败: {e}")

        return registered_count

    def get_registered_mcp_tools(self) -> list[str]:
        """获取所有已注册的 MCP 工具名称"""
        mcp_tools = []
        for tool_info in self._registry.list_tools():
            if tool_info.get("type") == "mcp":
                mcp_tools.append(tool_info["name"])
        return mcp_tools


def get_mcp_adapter() -> MCPAdapter:
    """获取 MCPAdapter 单例"""
    return MCPAdapter()
