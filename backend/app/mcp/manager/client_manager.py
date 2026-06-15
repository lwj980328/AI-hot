"""MCP Client Manager

统一管理所有 MCP Client 的生命周期。
对应 docs/06_MCP设计规范.md 第14节。
"""

import logging

from app.mcp.clients.base_client import BaseMCPClient
from app.mcp.clients.stdio_client import STDIOMCPClient
from app.mcp.schemas.config import MCPServerConfig

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP Client 管理器（单例）

    负责管理所有 MCP Client 的连接、断开、重连。
    """

    _instance: "MCPClientManager | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._clients: dict[str, BaseMCPClient] = {}
            cls._instance._configs: dict[str, MCPServerConfig] = {}
        return cls._instance

    @property
    def clients(self) -> dict[str, BaseMCPClient]:
        """获取所有客户端"""
        return self._clients

    def _create_client(self, config: MCPServerConfig) -> BaseMCPClient:
        """根据配置创建客户端实例"""
        if config.transport == "stdio":
            return STDIOMCPClient(config)
        # TODO: 后续支持 SSE 和 HTTP
        # elif config.transport == "sse":
        #     return SSEMCPClient(config)
        # elif config.transport == "http":
        #     return HTTPMCPClient(config)
        else:
            raise ValueError(f"不支持的传输协议: {config.transport}")

    async def add_client(self, config: MCPServerConfig) -> BaseMCPClient:
        """添加并连接一个 MCP Client

        Args:
            config: MCP Server 配置

        Returns:
            创建的客户端实例
        """
        if config.server_id in self._clients:
            logger.warning(f"MCP Client '{config.server_id}' 已存在，先移除旧连接")
            await self.remove_client(config.server_id)

        client = self._create_client(config)
        self._clients[config.server_id] = client
        self._configs[config.server_id] = config

        # 如果配置为启用，则自动连接
        if config.enabled:
            try:
                await client.connect()
            except FileNotFoundError as e:
                logger.error(f"MCP Client '{config.server_id}' 命令不存在: {e}")
                # 命令不存在不抛出异常，允许后续手动重连
            except Exception as e:
                logger.error(f"MCP Client '{config.server_id}' 自动连接失败: {e}")
                # 连接失败不影响注册，后续可手动重连

        return client

    async def remove_client(self, server_id: str) -> None:
        """移除并断开一个 MCP Client"""
        if server_id not in self._clients:
            return

        client = self._clients[server_id]
        try:
            await client.disconnect()
        except Exception as e:
            logger.warning(f"断开 MCP Client '{server_id}' 时出错: {e}")

        del self._clients[server_id]
        del self._configs[server_id]
        logger.info(f"MCP Client '{server_id}' 已移除")

    def get_client(self, server_id: str) -> BaseMCPClient | None:
        """获取指定的客户端"""
        return self._clients.get(server_id)

    def get_config(self, server_id: str) -> MCPServerConfig | None:
        """获取指定客户端的配置"""
        return self._configs.get(server_id)

    async def connect_all(self) -> dict[str, bool]:
        """连接所有客户端

        Returns:
            各客户端连接结果 {server_id: success}
        """
        results = {}
        for server_id, client in self._clients.items():
            if client.is_connected():
                results[server_id] = True
                continue
            try:
                await client.connect()
                results[server_id] = True
            except Exception as e:
                logger.error(f"MCP Client '{server_id}' 连接失败: {e}")
                results[server_id] = False
        return results

    async def disconnect_all(self) -> None:
        """断开所有客户端"""
        for server_id in list(self._clients.keys()):
            await self.remove_client(server_id)

    async def health_check(self) -> dict[str, bool]:
        """检查所有客户端连接状态"""
        return {sid: client.is_connected() for sid, client in self._clients.items()}

    async def reconnect(self, server_id: str) -> bool:
        """重连指定客户端"""
        if server_id not in self._clients:
            logger.error(f"MCP Client '{server_id}' 不存在")
            return False

        config = self._configs.get(server_id)
        if not config:
            logger.error(f"MCP Client '{server_id}' 配置不存在")
            return False

        # 先断开再重连
        await self.remove_client(server_id)
        try:
            await self.add_client(config)
            return True
        except Exception as e:
            logger.error(f"MCP Client '{server_id}' 重连失败: {e}")
            return False


def get_mcp_client_manager() -> MCPClientManager:
    """获取 MCPClientManager 单例"""
    return MCPClientManager()
