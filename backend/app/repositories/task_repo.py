from sqlalchemy import select, func
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

    async def delete_by_id(self, task_id: str) -> bool:
        """删除任务"""
        task = await self.get_by_id(task_id)
        if task:
            await self.session.delete(task)
            await self.session.flush()
            await self.session.commit()  # 显式提交事务
            return True
        return False

    async def count_all(self) -> int:
        """统计总任务数"""
        result = await self.session.execute(select(func.count(Task.id)))
        return result.scalar() or 0

    async def count_by_status(self, status: str) -> int:
        """按状态统计任务数"""
        result = await self.session.execute(
            select(func.count(Task.id)).where(Task.status == status)
        )
        return result.scalar() or 0
