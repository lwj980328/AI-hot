"""节点执行日志仓储"""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.node_execution_log import NodeExecutionLog
from app.repositories.base_repo import BaseRepository


class NodeExecutionLogRepository(BaseRepository[NodeExecutionLog]):
    """NodeExecutionLog仓储"""

    def __init__(self, session: AsyncSession):
        super().__init__(NodeExecutionLog, session)

    async def create_log(
        self,
        workflow_run_id: str,
        node_name: str,
        input_summary: str,
        output_summary: str,
        duration_ms: int = 0,
    ) -> NodeExecutionLog:
        """创建节点执行日志"""
        log = NodeExecutionLog(
            workflow_run_id=workflow_run_id,
            node_name=node_name,
            input_summary=input_summary,
            output_summary=output_summary,
            duration_ms=duration_ms,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_by_workflow_run(self, workflow_run_id: str) -> Sequence[NodeExecutionLog]:
        """获取工作流运行的所有节点执行日志"""
        result = await self.session.execute(
            select(NodeExecutionLog)
            .where(NodeExecutionLog.workflow_run_id == workflow_run_id)
            .order_by(NodeExecutionLog.created_at)
        )
        return result.scalars().all()
