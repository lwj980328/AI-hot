"""MCP Tool 实现

将 MCP Server 暴露的工具适配为 BaseTool 接口。
对应 docs/06_MCP设计规范.md 第17节。
对应 docs/03_工具设计规范.md 第8节。
"""

import asyncio
import logging
from typing import Any

from pydantic import BaseModel, Field, create_model

from app.mcp.clients.base_client import BaseMCPClient
from app.mcp.schemas.config import MCPServerConfig
from app.mcp.schemas.metadata import MCPToolMetadata
from app.tools.base.base_tool import BaseTool
from app.tools.base.exceptions import (
    ToolConnectionError,
    ToolError,
    ToolTimeoutError,
)

logger = logging.getLogger(__name__)


class MCPToolOutput(BaseModel):
    """MCP 工具输出模型"""

    result: Any = Field(None, description="执行结果")


class MCPTool(BaseTool):
    """MCP 工具适配器

    将 MCP Server 的工具包装为 BaseTool，对 Agent 完全透明。
    Agent 无法区分本地工具和 MCP 工具。

    异常处理遵循 docs/06_MCP设计规范.md 第21节：
    - MCP 不可用时抛出 ToolConnectionError
    - 超时时抛出 ToolTimeoutError
    - 禁止 Workflow 崩溃，由 ToolService 统一处理
    """

    def __init__(
        self,
        metadata: MCPToolMetadata,
        client: BaseMCPClient,
        server_config: MCPServerConfig | None = None,
    ):
        """
        Args:
            metadata: MCP 工具元数据
            client: MCP 客户端实例
            server_config: MCP Server 配置（用于获取 timeout 等参数）
        """
        # 设置工具基本信息
        self.name = f"mcp_{metadata.server_id}_{metadata.tool_name}"
        self.description = metadata.description or f"MCP 工具: {metadata.tool_name}"
        self.version = "0.1.0"

        # 保存 MCP 特有信息
        self._metadata = metadata
        self._client = client
        self._server_id = metadata.server_id
        self._tool_name = metadata.tool_name
        self._timeout = server_config.timeout if server_config else 30

        # 动态生成 input_schema
        self.input_schema = self._build_input_schema(metadata.input_schema)

        # 输出 schema
        self.output_schema = MCPToolOutput

    def _build_input_schema(self, json_schema: dict) -> type[BaseModel]:
        """根据 MCP 工具的 JSON Schema 动态构建 Pydantic 模型

        Args:
            json_schema: MCP 工具的 inputSchema

        Returns:
            动态生成的 Pydantic 模型类
        """
        if not json_schema or not json_schema.get("properties"):
            # 没有参数定义，返回空模型
            return create_model(f"{self.name}_input")

        fields = {}
        properties = json_schema.get("properties", {})
        required_fields = json_schema.get("required", [])

        for field_name, field_def in properties.items():
            field_type = self._json_type_to_python(field_def.get("type", "string"))
            description = field_def.get("description", "")
            default = field_def.get("default")

            if field_name in required_fields:
                # 必填字段
                fields[field_name] = (field_type, Field(..., description=description))
            else:
                # 可选字段
                default_value = default if default is not None else None
                fields[field_name] = (
                    field_type | None,
                    Field(default_value, description=description),
                )

        return create_model(f"{self.name}_input", **fields)

    @staticmethod
    def _json_type_to_python(json_type: str) -> type:
        """JSON Schema 类型转 Python 类型"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_mapping.get(json_type, str)

    async def execute(self, input_data: BaseModel) -> MCPToolOutput:
        """执行 MCP 工具

        Args:
            input_data: 工具输入参数

        Returns:
            MCPToolOutput: 执行结果

        Raises:
            ToolTimeoutError: 执行超时
            ToolConnectionError: MCP Server 连接失败
            ToolError: 其他工具执行错误
        """
        try:
            # 将 Pydantic 模型转为 dict
            arguments = input_data.model_dump(exclude_none=True)

            logger.info(f"调用 MCP 工具: {self._tool_name}, 参数: {arguments}")

            # 调用 MCP 工具（带超时控制）
            result = await asyncio.wait_for(
                self._client.call_tool(self._tool_name, arguments),
                timeout=self._timeout,
            )

            logger.info(f"MCP 工具 '{self._tool_name}' 执行成功")
            return MCPToolOutput(result=result)

        except asyncio.TimeoutError:
            error_msg = f"MCP 工具 '{self._tool_name}' 执行超时 ({self._timeout}s)"
            logger.error(error_msg)
            raise ToolTimeoutError(error_msg)

        except ConnectionError as e:
            error_msg = f"MCP 工具 '{self._tool_name}' 连接失败: {e}"
            logger.error(error_msg)
            raise ToolConnectionError(error_msg)

        except ToolError:
            # 已经是工具异常，直接抛出
            raise

        except Exception as e:
            error_msg = f"MCP 工具 '{self._tool_name}' 执行失败: {e}"
            logger.error(error_msg)
            raise ToolError(error_msg)

    def get_metadata(self) -> dict:
        """获取工具元数据，扩展基类方法"""
        base_metadata = super().get_metadata()
        base_metadata["mcp_server_id"] = self._server_id
        base_metadata["mcp_tool_name"] = self._tool_name
        base_metadata["type"] = "mcp"
        return base_metadata
