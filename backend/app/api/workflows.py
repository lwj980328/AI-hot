from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.schemas.api.task_request import RunWorkflowRequest
from app.schemas.api.task_response import WorkflowRunResponse
from app.services.workflow_service import WorkflowService
from app.services.exceptions import NotFoundError, WorkflowError

router = APIRouter()


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(
    request: RunWorkflowRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """执行研究工作流"""
    try:
        service = WorkflowService(session)
        return await service.run_task(request.task_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WorkflowError as e:
        raise HTTPException(status_code=500, detail=str(e))
