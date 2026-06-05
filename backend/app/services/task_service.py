import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository
from app.services.dto.task_dto import TaskDTO
from app.services.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class TaskService:
    """研究任务服务"""

    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def create_task(self, task_name: str, user_query: str) -> TaskDTO:
        """创建研究任务"""
        logger.info(f"创建任务: {task_name}")
        task = await self.repo.create(
            task_name=task_name,
            user_query=user_query,
            task_type="research",
            status="created",
        )
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
        return TaskDTO.model_validate(task)
