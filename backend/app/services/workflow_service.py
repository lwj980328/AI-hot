import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repo import TaskRepository
from app.repositories.workflow_run_repo import WorkflowRunRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.tool_execution_log_repo import ToolExecutionLogRepository
from app.schemas.state.agent_state import TaskStatus
from app.services.dto.task_dto import WorkflowRunDTO
from app.services.exceptions import NotFoundError, WorkflowError
from app.workflows.research.manager import ResearchWorkflowManager
from app.workflows.research.graph import set_workflow_context
from app.workflows.base.workflow_context import WorkflowContext

logger = logging.getLogger(__name__)


class WorkflowService:
    """工作流服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.run_repo = WorkflowRunRepository(session)
        self.report_repo = ReportRepository(session)
        self.tool_log_repo = ToolExecutionLogRepository(session)

    async def get_runs_by_task(self, task_id: str) -> list[WorkflowRunDTO]:
        """获取任务的所有运行记录"""
        runs = await self.run_repo.get_runs_by_task(task_id)
        return [WorkflowRunDTO.model_validate(run) for run in runs]

    async def get_workflow_status(self, task_id: str) -> dict:
        """获取工作流执行状态

        返回：
        - task_id: 任务 ID
        - task_status: 任务状态
        - current_node: 当前执行的节点（根据任务状态推断）
        - node_states: 各节点状态映射
        - tool_calls: 工具调用历史（从 tool_execution_logs 表查询）
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", task_id)

        # 获取最新的工作流运行记录
        latest_run = await self.run_repo.get_latest_by_task(task_id)

        # 从独立的 tool_execution_logs 表获取工具调用记录
        tool_calls = []
        if latest_run:
            logs = await self.tool_log_repo.get_by_workflow_run(latest_run.id)
            tool_calls = [
                {
                    "node_name": log.node_name,
                    "tool_name": log.tool_name,
                    "input_params": log.input_params,
                    "output_summary": log.output_summary,
                    "success": log.success,
                    "duration_ms": log.duration_ms,
                    "called_at": log.called_at.isoformat() if log.called_at else None,
                }
                for log in logs
            ]

        # 节点执行顺序
        node_order = ["planner", "context", "research", "analysis", "memory", "report"]

        # 任务状态到节点的映射（根据任务状态推断当前节点，不依赖 AgentState.current_node）
        status_to_node = {
            "planning": "planner",
            "context_loading": "context",
            "researching": "research",
            "analyzing": "analysis",
            "memory_updating": "memory",
            "reporting": "report",
        }

        node_states = {}
        current_node = ""
        task_status = task.status

        # 确定当前节点
        if task_status in status_to_node:
            current_node = status_to_node[task_status]

        # 确定各节点状态
        if task_status == "created":
            # 所有节点等待中
            for node_name in node_order:
                node_states[node_name] = "pending"
        elif task_status == "completed":
            # 所有节点已完成
            for node_name in node_order:
                node_states[node_name] = "completed"
        elif task_status == "failed":
            # 所有节点失败
            for node_name in node_order:
                node_states[node_name] = "failed"
        else:
            # 正在执行中
            current_index = node_order.index(current_node) if current_node in node_order else -1
            for i, node_name in enumerate(node_order):
                if i < current_index:
                    node_states[node_name] = "completed"
                elif i == current_index:
                    node_states[node_name] = "running"
                else:
                    node_states[node_name] = "pending"

        return {
            "task_id": task_id,
            "task_status": task_status,
            "current_node": current_node,
            "node_states": node_states,
            "tool_calls": tool_calls,
        }

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
            status=TaskStatus.RESEARCHING.value,
        )

        # 3. 更新任务状态
        await self.task_repo.update_status(task_id, TaskStatus.RESEARCHING.value)
        await self.session.commit()

        # 4. 创建 WorkflowContext（依赖注入，替代全局变量）
        async def update_status_callback(tid: str, status: str) -> None:
            try:
                await self.task_repo.update_status(tid, status)
                await self.session.commit()
                logger.info(f"任务状态已更新: {tid} -> {status}")
            except Exception as e:
                logger.warning(f"更新任务状态失败: {e}")
                try:
                    await self.session.rollback()
                except Exception:
                    pass

        async def save_tool_calls_callback(tid: str, tool_calls: list) -> None:
            try:
                # 获取最新的工作流运行记录
                latest_run = await self.run_repo.get_latest_by_task(tid)
                if latest_run:
                    await self.tool_log_repo.create_batch(latest_run.id, tool_calls)
                    await self.session.commit()
                    logger.info(f"工具调用记录已保存: {len(tool_calls)} 条")
            except Exception as e:
                logger.warning(f"保存工具调用记录失败: {e}")
                try:
                    await self.session.rollback()
                except Exception:
                    pass

        workflow_context = WorkflowContext(
            task_id=task_id,
            status_callback=update_status_callback,
            tool_calls_callback=save_tool_calls_callback,
        )
        set_workflow_context(workflow_context)

        # 5. 执行工作流
        try:
            manager = ResearchWorkflowManager()
            final_state = await manager.run(task_id, task.user_query)

            logger.info(
                f"工作流执行完成: task_id={task_id}, "
                f"report_title={final_state.report.title}, "
                f"report_summary_len={len(final_state.report.summary)}, "
                f"report_content_len={len(final_state.report.markdown_content)}"
            )

            # 6. 保存报告（如果已存在则更新）
            existing_report = await self.report_repo.get_by_task_id(task_id)
            if existing_report:
                existing_report.title = final_state.report.title or f"{task.user_query}研究报告"
                existing_report.summary = final_state.report.summary or ""
                existing_report.markdown_content = final_state.report.markdown_content or ""
                await self.session.flush()
                report = existing_report
                logger.info(f"报告已更新: report_id={report.id}")
            else:
                report = await self.report_repo.create(
                    task_id=task_id,
                    title=final_state.report.title or f"{task.user_query}研究报告",
                    summary=final_state.report.summary or "",
                    markdown_content=final_state.report.markdown_content or "",
                )
                logger.info(f"报告已保存: report_id={report.id}")

            # 7. 更新状态
            await self.run_repo.finish_run(run.id)
            await self.task_repo.update_status(task_id, TaskStatus.COMPLETED.value)
            await self.session.commit()

            logger.info(f"工作流执行成功: {task_id}")
            return WorkflowRunDTO.model_validate(run)

        except Exception as e:
            # 失败处理
            logger.exception(f"工作流执行失败: {task_id}")
            try:
                await self.run_repo.fail_run(run.id, str(e))
                await self.task_repo.update_status(task_id, TaskStatus.FAILED.value)
                await self.session.commit()
            except Exception as inner_e:
                logger.error(f"更新失败状态也出错: {inner_e}")
            raise WorkflowError(f"工作流执行失败: {str(e)}")
