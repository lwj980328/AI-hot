from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    task_name: str
    user_query: str


class RunWorkflowRequest(BaseModel):
    """运行工作流请求"""
    task_id: str
