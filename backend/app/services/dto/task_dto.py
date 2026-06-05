from datetime import datetime
from pydantic import BaseModel


class TaskDTO(BaseModel):
    """任务数据传输对象"""
    id: str
    task_name: str
    user_query: str
    task_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunDTO(BaseModel):
    """工作流运行数据传输对象"""
    id: str
    task_id: str
    run_number: int
    trigger_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ReportDTO(BaseModel):
    """报告数据传输对象"""
    id: str
    task_id: str
    title: str
    summary: str
    markdown_content: str
    created_at: datetime

    model_config = {"from_attributes": True}
