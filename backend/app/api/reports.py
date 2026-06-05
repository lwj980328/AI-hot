from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.schemas.api.task_response import ReportResponse
from app.services.report_service import ReportService
from app.services.exceptions import NotFoundError

router = APIRouter()


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """获取报告详情"""
    try:
        service = ReportService(session)
        return await service.get_report(report_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/by-task/{task_id}", response_model=ReportResponse)
async def get_report_by_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """根据任务ID获取报告"""
    try:
        service = ReportService(session)
        return await service.get_report_by_task(task_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
