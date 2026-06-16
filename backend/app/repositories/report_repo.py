from sqlalchemy import select, func
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

    async def count_all(self) -> int:
        """统计总报告数"""
        result = await self.session.execute(select(func.count(Report.id)))
        return result.scalar() or 0
