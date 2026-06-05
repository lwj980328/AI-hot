from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.report import Report
from app.repositories.base_repo import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """Report仓储"""

    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)

    async def get_by_task_id(self, task_id: str) -> Report | None:
        """根据任务ID查询报告"""
        result = await self.session.execute(
            select(Report).where(Report.task_id == task_id)
        )
        return result.scalar_one_or_none()
