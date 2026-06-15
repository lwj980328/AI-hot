"""ToolRegistry 工具注册表

统一管理所有工具的注册与发现。
对应 docs/03_工具设计规范.md 第10-11节。
"""

import logging
from app.tools.base.base_tool import BaseTool
from app.tools.base.exceptions import ToolNotFoundError

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具注册表（单例）

    所有工具必须在此注册后才能被 Agent 调用。
    """

    _instance: "ToolRegistry | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: dict[str, BaseTool] = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """注册一个工具"""
        if not isinstance(tool, BaseTool):
            raise TypeError("ToolRegistry 只能注册 BaseTool 实例")

        if tool.name in self._tools:
            logger.warning(f"ToolRegistry: 工具 '{tool.name}' 已存在，覆盖注册")

        self._tools[tool.name] = tool
        logger.info(f"ToolRegistry: 注册工具 '{tool.name}' v{tool.version}")

    def get_tool(self, name: str) -> BaseTool:
        """根据名称获取工具"""
        if name not in self._tools:
            raise ToolNotFoundError(f"工具未注册: {name}")
        return self._tools[name]

    def list_tools(self) -> list[dict]:
        """列出所有已注册工具的元数据"""
        return [tool.get_metadata() for tool in self._tools.values()]

    def has_tool(self, name: str) -> bool:
        """检查工具是否已注册"""
        return name in self._tools


def get_tool_registry() -> ToolRegistry:
    """获取 ToolRegistry 单例"""
    return ToolRegistry()
