from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.workflow_run import WorkflowRun
from app.repositories.base_repo import BaseRepository


class WorkflowRunRepository(BaseRepository[WorkflowRun]):
    """WorkflowRun仓储"""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkflowRun, session)

    async def finish_run(self, run_id: str) -> WorkflowRun | None:
        """完成工作流运行"""
        run = await self.get_by_id(run_id)
        if run:
            run.status = "completed"
            run.finished_at = datetime.now()
            await self.session.flush()
        return run

    async def fail_run(self, run_id: str, error_message: str) -> WorkflowRun | None:
        """标记工作流运行失败"""
        run = await self.get_by_id(run_id)
        if run:
            run.status = "failed"
            run.finished_at = datetime.now()
            run.error_message = error_message
            await self.session.flush()
        return run

    async def get_latest_by_task(self, task_id: str) -> WorkflowRun | None:
        """获取任务最新的运行记录"""
        result = await self.session.execute(
            select(WorkflowRun)
            .where(WorkflowRun.task_id == task_id)
            .order_by(WorkflowRun.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
