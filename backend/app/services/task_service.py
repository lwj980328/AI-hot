import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository
from app.repositories.report_repo import ReportRepository
from app.services.dto.task_dto import TaskDTO
from app.services.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class TaskService:
    """研究任务服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TaskRepository(session)
        self.report_repo = ReportRepository(session)

    async def create_task(self, user_query: str, task_name: str | None = None) -> TaskDTO:
        """创建研究任务"""
        task_name = task_name or user_query
        logger.info(f"创建任务: {task_name}")
        task = await self.repo.create(
            task_name=task_name,
            user_query=user_query,
            task_type="research",
            status="created",
        )
        await self.session.commit()
        return TaskDTO.model_validate(task)

    async def get_task(self, task_id: str) -> TaskDTO:
        """获取任务详情"""
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", task_id)
        return TaskDTO.model_validate(task)

    async def list_tasks(self, limit: int = 20, offset: int = 0) -> list[TaskDTO]:
        """获取任务列表"""
        tasks = await self.repo.list_all(limit=limit, offset=offset)
        return [TaskDTO.model_validate(t) for t in tasks]

    async def update_status(self, task_id: str, status: str) -> TaskDTO:
        """更新任务状态"""
        logger.info(f"更新任务状态: {task_id} -> {status}")
        task = await self.repo.update_status(task_id, status)
        if not task:
            raise NotFoundError("Task", task_id)
        await self.session.commit()
        return TaskDTO.model_validate(task)

    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        logger.info(f"删除任务: {task_id}")
        deleted = await self.repo.delete_by_id(task_id)
        if not deleted:
            raise NotFoundError("Task", task_id)
        await self.session.commit()
        return True

    async def get_stats(self) -> dict:
        """获取任务统计（全量数据）"""
        total_tasks = await self.repo.count_all()
        completed_tasks = await self.repo.count_by_status("completed")
        failed_tasks = await self.repo.count_by_status("failed")
        running_tasks = await self.repo.count_by_status("running")
        total_reports = await self.report_repo.count_all()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "total_reports": total_reports,
        }
