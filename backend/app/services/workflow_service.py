import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository
from app.repositories.workflow_run_repo import WorkflowRunRepository
from app.repositories.report_repo import ReportRepository
from app.services.dto.task_dto import WorkflowRunDTO
from app.services.exceptions import NotFoundError, WorkflowError
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

        # 4. 执行工作流（task_id 和 user_query 由 Manager 内部构建 AgentState）
        try:
            manager = ResearchWorkflowManager()
            final_state = await manager.run(task_id, task.user_query)

            logger.info(
                f"工作流执行完成: task_id={task_id}, "
                f"report_title={final_state.report.title}, "
                f"report_summary_len={len(final_state.report.summary)}, "
                f"report_content_len={len(final_state.report.markdown_content)}"
            )

            # 5. 保存报告
            report = await self.report_repo.create(
                task_id=task_id,
                title=final_state.report.title or f"{task.user_query}研究报告",
                summary=final_state.report.summary or "",
                markdown_content=final_state.report.markdown_content or "",
            )
            logger.info(f"报告已保存: report_id={report.id}")

            # 6. 更新状态
            await self.run_repo.finish_run(run.id)
            await self.task_repo.update_status(task_id, "completed")

            logger.info(f"工作流执行成功: {task_id}")
            return WorkflowRunDTO.model_validate(run)

        except Exception as e:
            # 失败处理
            logger.exception(f"工作流执行失败: {task_id}")
            try:
                await self.run_repo.fail_run(run.id, str(e))
                await self.task_repo.update_status(task_id, "failed")
            except Exception as inner_e:
                logger.error(f"更新失败状态也出错: {inner_e}")
            raise WorkflowError(f"工作流执行失败: {str(e)}")
