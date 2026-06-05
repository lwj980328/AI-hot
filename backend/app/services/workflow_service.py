import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository
from app.repositories.workflow_run_repo import WorkflowRunRepository
from app.repositories.report_repo import ReportRepository
from app.services.dto.task_dto import WorkflowRunDTO
from app.services.exceptions import NotFoundError, WorkflowError
from app.schemas.state.agent_state import AgentState
from app.workflows.research.manager import ResearchWorkflowManager

logger = logging.getLogger(__name__)


class WorkflowService:
    """工作流服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.run_repo = WorkflowRunRepository(session)
        self.report_repo = ReportRepository(session)

    async def run_task(self, task_id: str) -> WorkflowRunDTO:
        """执行研究任务的工作流"""
        # 1. 获取任务
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", task_id)

        # 2. 创建工作流运行记录
        run = await self.run_repo.create(
            task_id=task_id,
            run_number=1,
            trigger_type="api",
            status="running",
        )

        # 3. 更新任务状态
        await self.task_repo.update_status(task_id, "running")

        # 4. 构建初始状态
        initial_state = AgentState(
            task_id=task_id,
            user_query=task.user_query,
        )

        # 5. 执行工作流
        try:
            manager = ResearchWorkflowManager()
            final_state = await manager.run(initial_state)

            # 6. 保存报告
            await self.report_repo.create(
                task_id=task_id,
                title=final_state.report.title,
                summary=final_state.report.summary,
                markdown_content=final_state.report.markdown_content,
            )

            # 7. 更新状态
            await self.run_repo.finish_run(run.id)
            await self.task_repo.update_status(task_id, "completed")

            logger.info(f"工作流执行成功: {task_id}")
            return WorkflowRunDTO.model_validate(run)

        except Exception as e:
            # 失败处理
            await self.run_repo.fail_run(run.id, str(e))
            await self.task_repo.update_status(task_id, "failed")
            logger.error(f"工作流执行失败: {task_id}, 错误: {e}")
            raise WorkflowError(f"工作流执行失败: {str(e)}")
