import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ToolExecutionLog(Base):
    """工具执行记录表

    独立存储每次工具调用的详细信息，遵循 07_数据库设计.md 规范。
    """
    __tablename__ = "tool_execution_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workflow_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    node_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_summary: Mapped[str] = mapped_column(String(500), default="")
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    called_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # 关系
    workflow_run: Mapped["WorkflowRun"] = relationship(back_populates="tool_logs")
