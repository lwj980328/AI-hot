from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import Task
from app.repositories.base_repo import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Task仓储"""

    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def update_status(self, task_id: str, status: str) -> Task | None:
        """更新任务状态"""
        task = await self.get_by_id(task_id)
        if task:
            task.status = status
            await self.session.flush()
        return task
