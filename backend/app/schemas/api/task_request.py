from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    task_name: str | None = Field(default=None, description="任务名称，未提供时使用 user_query")
    user_query: str


class RunWorkflowRequest(BaseModel):
    """运行工作流请求"""
    task_id: str
