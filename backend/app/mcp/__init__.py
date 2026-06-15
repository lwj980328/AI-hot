"""MCP 模块

Model Context Protocol 能力接入层。
对应 docs/06_MCP设计规范.md。
"""

from app.mcp.schemas import MCPServerConfig, MCPToolMetadata
from app.mcp.clients import BaseMCPClient, STDIOMCPClient
from app.mcp.manager import MCPClientManager, get_mcp_client_manager
from app.mcp.discovery import MCPDiscoveryService, get_mcp_discovery_service
from app.mcp.adapters import MCPAdapter, get_mcp_adapter
from app.mcp.tools import MCPTool

__all__ = [
    "MCPServerConfig",
    "MCPToolMetadata",
    "BaseMCPClient",
    "STDIOMCPClient",
    "MCPClientManager",
    "get_mcp_client_manager",
    "MCPDiscoveryService",
    "get_mcp_discovery_service",
    "MCPAdapter",
    "get_mcp_adapter",
    "MCPTool",
]
