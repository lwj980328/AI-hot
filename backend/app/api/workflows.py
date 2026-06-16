from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.schemas.api.task_request import RunWorkflowRequest
from app.schemas.api.task_response import WorkflowRunResponse
from app.schemas.api.common import ApiResponse
from app.services.workflow_service import WorkflowService
from app.services.exceptions import NotFoundError, WorkflowError

router = APIRouter()


@router.post("/run", response_model=ApiResponse[WorkflowRunResponse])
async def run_workflow(
    request: RunWorkflowRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """执行研究工作流"""
    try:
        service = WorkflowService(session)
        run = await service.run_task(request.task_id)
        return ApiResponse.ok(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WorkflowError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{task_id}", response_model=ApiResponse[list[WorkflowRunResponse]])
async def get_workflow_runs(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务的工作流运行记录"""
    service = WorkflowService(session)
    runs = await service.get_runs_by_task(task_id)
    return ApiResponse.ok(runs)


@router.get("/status/{task_id}")
async def get_workflow_status(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """获取工作流执行状态（M7 新增）

    返回当前节点、各节点状态等信息，用于前端 Workflow 可视化。
    """
    try:
        service = WorkflowService(session)
        status = await service.get_workflow_status(task_id)
        return ApiResponse.ok(status)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
