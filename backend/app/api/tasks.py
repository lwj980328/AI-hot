from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.schemas.api.task_request import CreateTaskRequest
from app.schemas.api.task_response import TaskResponse
from app.services.task_service import TaskService
from app.services.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """创建研究任务"""
    try:
        service = TaskService(session)
        task = await service.create_task(
            task_name=request.task_name,
            user_query=request.user_query,
        )
        return task
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务列表"""
    service = TaskService(session)
    tasks = await service.list_tasks(limit=limit, offset=offset)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务详情"""
    try:
        service = TaskService(session)
        return await service.get_task(task_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
