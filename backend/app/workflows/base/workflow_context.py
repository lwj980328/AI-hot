"""工作流上下文

遵循 04_Workflow设计规范.md，通过依赖注入传递回调，
避免使用全局共享变量。
"""

from dataclasses import dataclass, field
from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkflowContext:
    """工作流上下文，封装工作流执行过程中需要的外部依赖

    通过依赖注入方式传递给节点函数，避免使用全局变量。
    """

    task_id: str = ""

    # 任务状态更新回调
    status_callback: Callable[[str, str], Awaitable[None]] | None = None

    # 工具调用记录保存回调
    tool_calls_callback: Callable[[str, list], Awaitable[None]] | None = None

    async def update_status(self, status: str) -> None:
        """更新任务状态"""
        if self.status_callback and self.task_id:
            try:
                await self.status_callback(self.task_id, status)
            except Exception as e:
                logger.warning(f"更新任务状态失败: {e}")

    async def save_tool_calls(self, tool_calls: list) -> None:
        """保存工具调用记录"""
        if self.tool_calls_callback and self.task_id and tool_calls:
            try:
                await self.tool_calls_callback(self.task_id, tool_calls)
            except Exception as e:
                logger.warning(f"保存工具调用记录失败: {e}")
