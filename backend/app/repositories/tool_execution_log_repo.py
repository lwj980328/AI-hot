"""工具执行记录仓储"""

from typing import Sequence
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.tool_execution_log import ToolExecutionLog
from app.repositories.base_repo import BaseRepository


class ToolExecutionLogRepository(BaseRepository[ToolExecutionLog]):
    """ToolExecutionLog仓储"""

    def __init__(self, session: AsyncSession):
        super().__init__(ToolExecutionLog, session)

    async def create_batch(self, workflow_run_id: str, tool_calls: list[dict]) -> list[ToolExecutionLog]:
        """批量创建工具执行记录"""
        logs = []
        for call in tool_calls:
            log = ToolExecutionLog(
                workflow_run_id=workflow_run_id,
                node_name=call.get("node_name", ""),
                tool_name=call.get("tool_name", ""),
                input_params=call.get("input_params"),
                output_summary=call.get("output_summary", ""),
                success=call.get("success", True),
                duration_ms=call.get("duration_ms", 0),
            )
            self.session.add(log)
            logs.append(log)
        await self.session.flush()
        return logs

    async def get_by_workflow_run(self, workflow_run_id: str) -> Sequence[ToolExecutionLog]:
        """获取工作流运行的所有工具执行记录"""
        result = await self.session.execute(
            select(ToolExecutionLog)
            .where(ToolExecutionLog.workflow_run_id == workflow_run_id)
            .order_by(ToolExecutionLog.called_at)
        )
        return result.scalars().all()
