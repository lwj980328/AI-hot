"""ToolService 工具执行服务

统一执行入口：负责从 Registry 获取工具、校验输入、捕获异常、重试、超时降级。
对应 docs/03_工具设计规范.md 第4节与第14节。
"""

import asyncio
import logging
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.tools.base.base_tool import BaseTool
from app.tools.base.registry import ToolRegistry
from app.tools.base.exceptions import (
    ToolError,
    ToolNotFoundError,
    ToolValidationError,
)

logger = logging.getLogger(__name__)


class ToolService:
    """工具执行服务（单例）

    Agent 不直接调用 Tool，而是通过 ToolService.execute() 间接调用。
    """

    _instance: "ToolService | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.registry = ToolRegistry()
            cls._instance.settings = get_settings()
        return cls._instance

    async def execute(
        self,
        tool_name: str,
        input_data: BaseModel,
    ) -> BaseModel:
        """执行指定工具

        Args:
            tool_name: 工具名称
            input_data: 工具输入（Pydantic Model）

        Returns:
            工具输出（Pydantic Model）

        Raises:
            ToolNotFoundError: 工具未注册
            ToolValidationError: 输入/输出校验失败
            ToolError: 工具执行异常（已转换）
        """
        tool = self.registry.get_tool(tool_name)
        self._validate_input(tool, input_data)

        max_retries = getattr(self.settings, "tool_max_retries", 3)
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                output = await tool.execute(input_data)
                self._validate_output(tool, output)
                return output
            except ToolError as e:
                last_error = e
                logger.warning(
                    f"ToolService: {tool_name} 执行失败 (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # 指数退避：1s, 2s, 4s
            except ValidationError as e:
                logger.error(f"ToolService: {tool_name} 输出校验失败: {e}")
                raise ToolValidationError(f"{tool_name} 输出校验失败: {e}") from e
            except Exception as e:
                logger.error(f"ToolService: {tool_name} 发生未预期异常: {e}")
                raise ToolError(f"{tool_name} 执行异常: {e}") from e

        logger.error(f"ToolService: {tool_name} 在 {max_retries + 1} 次尝试后仍失败")
        raise last_error or ToolError(f"{tool_name} 执行失败")

    def _validate_input(self, tool: BaseTool, input_data: BaseModel) -> None:
        """校验输入类型是否匹配工具期望"""
        if not isinstance(input_data, tool.input_schema):
            raise ToolValidationError(
                f"{tool.name} 输入类型错误: "
                f"期望 {tool.input_schema.__name__}, 实际 {type(input_data).__name__}"
            )

    def _validate_output(self, tool: BaseTool, output: BaseModel) -> None:
        """校验输出类型是否匹配工具声明"""
        if not isinstance(output, tool.output_schema):
            raise ToolValidationError(
                f"{tool.name} 输出类型错误: "
                f"期望 {tool.output_schema.__name__}, 实际 {type(output).__name__}"
            )

    def list_available_tools(self) -> list[dict]:
        """列出所有可用工具"""
        return self.registry.list_tools()

    def register_local_tools(self) -> int:
        """注册所有本地工具

        遵循 docs/03_工具设计规范.md，统一管理工具注册。
        避免在 main.py 中直接实例化具体工具。

        Returns:
            注册的工具数量
        """
        from app.tools.arxiv import ArxivTool
        from app.tools.github import GithubTool
        from app.tools.web import WebSearchTool
        from app.tools.huggingface import HuggingFaceTool

        tools = [
            ArxivTool(),
            GithubTool(),
            WebSearchTool(),
            HuggingFaceTool(),
        ]

        for tool in tools:
            self.registry.register(tool)

        logger.info(f"本地工具注册完成，共 {len(tools)} 个")
        return len(tools)


def get_tool_service() -> ToolService:
    """获取 ToolService 单例"""
    return ToolService()
