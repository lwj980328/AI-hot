"""MCP Tool 元数据模型

对应 docs/06_MCP设计规范.md 第8节。
描述 MCP Server 暴露的工具能力。
"""

from pydantic import BaseModel, Field


class MCPToolMetadata(BaseModel):
    """MCP 工具元数据

    对应 docs/06_MCP设计规范.md 第8节 MCPToolMetadata 定义。
    """

    tool_name: str = Field(..., description="工具名称")
    description: str = Field("", description="工具描述")
    input_schema: dict = Field(default_factory=dict, description="输入参数 JSON Schema")
    output_schema: dict = Field(default_factory=dict, description="输出参数 JSON Schema")
    server_id: str = Field(..., description="所属 MCP Server ID")
