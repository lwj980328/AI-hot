"""工具列表 API

暴露已注册的工具信息，包括本地工具和 MCP 工具。
"""

from fastapi import APIRouter
from app.tools.base.registry import get_tool_registry
from app.schemas.api.common import ApiResponse

router = APIRouter()


@router.get("")
async def list_tools():
    """获取所有已注册工具的列表"""
    registry = get_tool_registry()
    tools = registry.list_tools()

    # 分类统计
    local_tools = [t for t in tools if t.get("type") != "mcp"]
    mcp_tools = [t for t in tools if t.get("type") == "mcp"]

    data = {
        "total": len(tools),
        "local_count": len(local_tools),
        "mcp_count": len(mcp_tools),
        "tools": tools,
    }
    return ApiResponse.ok(data)


@router.get("/{tool_name}")
async def get_tool(tool_name: str):
    """获取指定工具的详细信息"""
    registry = get_tool_registry()

    if not registry.has_tool(tool_name):
        return ApiResponse.error(f"工具 '{tool_name}' 未注册")

    tool = registry.get_tool(tool_name)
    return ApiResponse.ok(tool.get_metadata())
