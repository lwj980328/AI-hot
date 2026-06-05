from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.state.research_state import ResearchState
from app.schemas.state.context_state import ContextState
from app.schemas.state.analysis_state import AnalysisState
from app.schemas.state.memory_state import MemoryState
from app.schemas.state.report_state import ReportState


class TaskStatus(str, Enum):
    """任务状态枚举"""
    CREATED = "created"
    PLANNING = "planning"
    CONTEXT_LOADING = "context_loading"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    MEMORY_UPDATING = "memory_updating"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorInfo(BaseModel):
    """错误信息"""
    error_type: str = ""
    error_message: str = ""
    node_name: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """系统唯一状态载体"""
    task_id: str = ""
    user_query: str = ""
    status: TaskStatus = TaskStatus.CREATED

    # 子状态模块
    research: ResearchState = Field(default_factory=ResearchState)
    context: ContextState = Field(default_factory=ContextState)
    analysis: AnalysisState = Field(default_factory=AnalysisState)
    memory: MemoryState = Field(default_factory=MemoryState)
    report: ReportState = Field(default_factory=ReportState)

    # 错误信息
    error_info: ErrorInfo | None = None
