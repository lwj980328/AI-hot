"""MCP Discovery Service

系统启动时自动发现 MCP Server 暴露的工具能力。
对应 docs/06_MCP设计规范.md 第15节。
"""

import logging
from pathlib import Path

import yaml

from app.mcp.manager.client_manager import MCPClientManager, get_mcp_client_manager
from app.mcp.schemas.config import MCPServerConfig
from app.mcp.schemas.metadata import MCPToolMetadata

logger = logging.getLogger(__name__)

# 默认配置目录路径
DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config" / "mcp"


class MCPDiscoveryService:
    """MCP 工具发现服务

    负责：
    1. 加载 MCP Server 配置
    2. 连接 MCP Server
    3. 发现并返回工具元数据

    配置目录结构遵循 docs/06_MCP设计规范.md 第23节：
    backend/config/mcp/
    ├── github.yaml
    ├── search.yaml
    ├── filesystem.yaml
    └── ...
    """

    def __init__(self, client_manager: MCPClientManager | None = None):
        self._client_manager = client_manager or get_mcp_client_manager()

    def load_configs(self, config_dir: Path | str | None = None) -> list[MCPServerConfig]:
        """从配置目录加载所有 MCP Server 配置

        遵循 docs/06_MCP设计规范.md 第23节，每个 MCP Server 一个独立配置文件。

        Args:
            config_dir: 配置目录路径，默认使用 backend/config/mcp/

        Returns:
            配置列表
        """
        config_dir = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR

        if not config_dir.exists():
            logger.warning(f"MCP 配置目录不存在: {config_dir}")
            return []

        configs = []
        yaml_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if not data:
                    logger.warning(f"MCP 配置文件为空: {yaml_file}")
                    continue

                # 支持两种格式：
                # 1. 单个 server 配置（直接是字段）
                # 2. 多个 server 配置（servers 数组）
                if "server_id" in data:
                    # 单个 server 配置
                    config = MCPServerConfig(**data)
                    configs.append(config)
                elif "servers" in data:
                    # 多个 server 配置
                    for server_data in data["servers"]:
                        config = MCPServerConfig(**server_data)
                        configs.append(config)
                else:
                    logger.warning(f"MCP 配置文件格式错误: {yaml_file}")
                    continue

            except Exception as e:
                logger.error(f"加载 MCP 配置文件失败 {yaml_file}: {e}")
                continue

        logger.info(f"加载了 {len(configs)} 个 MCP Server 配置")
        return configs

    async def init_from_config(self, config_dir: Path | str | None = None) -> None:
        """从配置目录初始化所有 MCP Client

        Args:
            config_dir: 配置目录路径
        """
        configs = self.load_configs(config_dir)

        for config in configs:
            if not config.enabled:
                logger.info(f"MCP Server '{config.server_id}' 已禁用，跳过")
                continue

            try:
                await self._client_manager.add_client(config)
            except Exception as e:
                logger.error(f"初始化 MCP Server '{config.server_id}' 失败: {e}")

    async def discover(self, server_id: str) -> list[MCPToolMetadata]:
        """发现指定 MCP Server 的工具

        Args:
            server_id: MCP Server ID

        Returns:
            工具元数据列表
        """
        client = self._client_manager.get_client(server_id)
        if not client:
            logger.error(f"MCP Client '{server_id}' 不存在")
            return []

        if not client.is_connected():
            logger.warning(f"MCP Client '{server_id}' 未连接，尝试重连")
            try:
                success = await self._client_manager.reconnect(server_id)
                if not success:
                    return []
                client = self._client_manager.get_client(server_id)
            except Exception as e:
                logger.error(f"MCP Client '{server_id}' 重连失败: {e}")
                return []

        try:
            tools = await client.list_tools()
            logger.info(f"MCP Server '{server_id}' 发现 {len(tools)} 个工具")
            return tools
        except Exception as e:
            logger.error(f"发现 MCP Server '{server_id}' 工具失败: {e}")
            return []

    async def discover_all(self) -> dict[str, list[MCPToolMetadata]]:
        """发现所有已连接 MCP Server 的工具

        Returns:
            {server_id: [tool_metadata, ...]}
        """
        results = {}

        for server_id, client in self._client_manager.clients.items():
            if not client.is_connected():
                logger.warning(f"MCP Client '{server_id}' 未连接，跳过")
                continue

            tools = await self.discover(server_id)
            results[server_id] = tools

        return results


def get_mcp_discovery_service() -> MCPDiscoveryService:
    """获取 MCPDiscoveryService 单例"""
    return MCPDiscoveryService()
