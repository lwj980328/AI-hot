from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.schemas.api.task_request import CreateTaskRequest
from app.schemas.api.task_response import TaskResponse, TaskStatsResponse
from app.schemas.api.common import ApiResponse
from app.services.task_service import TaskService
from app.services.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("", response_model=ApiResponse[TaskResponse])
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
        return ApiResponse.ok(task)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ApiResponse[list[TaskResponse]])
async def list_tasks(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务列表"""
    service = TaskService(session)
    tasks = await service.list_tasks(limit=limit, offset=offset)
    return ApiResponse.ok(tasks)


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务详情"""
    try:
        service = TaskService(session)
        task = await service.get_task(task_id)
        return ApiResponse.ok(task)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """删除任务"""
    try:
        service = TaskService(session)
        await service.delete_task(task_id)
        return ApiResponse.ok(None, message="任务已删除")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/overview", response_model=ApiResponse[TaskStatsResponse])
async def get_task_stats(
    session: AsyncSession = Depends(get_db_session),
):
    """获取任务统计（全量数据）"""
    service = TaskService(session)
    stats = await service.get_stats()
    return ApiResponse.ok(stats)
