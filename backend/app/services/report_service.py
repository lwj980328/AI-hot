import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.report_repo import ReportRepository
from app.services.dto.task_dto import ReportDTO
from app.services.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class ReportService:
    """研究报告服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ReportRepository(session)

    async def get_report(self, report_id: str) -> ReportDTO:
        """获取报告详情"""
        report = await self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundError("Report", report_id)
        return ReportDTO.model_validate(report)

    async def get_report_by_task(self, task_id: str) -> ReportDTO:
        """根据任务ID获取报告"""
        report = await self.repo.get_by_task_id(task_id)
        if not report:
            raise NotFoundError("Report", f"task_id={task_id}")
        return ReportDTO.model_validate(report)
