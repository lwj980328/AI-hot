import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class WorkflowRun(Base):
    """工作流执行记录表"""
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    run_number: Mapped[int] = mapped_column(Integer, default=1)
    trigger_type: Mapped[str] = mapped_column(String(50), default="manual")
    status: Mapped[str] = mapped_column(String(50), default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # 关系
    task: Mapped["Task"] = relationship(back_populates="workflow_runs")
    tool_logs: Mapped[list["ToolExecutionLog"]] = relationship(
        back_populates="workflow_run", cascade="all, delete-orphan"
    )
    node_logs: Mapped[list["NodeExecutionLog"]] = relationship(
        back_populates="workflow_run", cascade="all, delete-orphan"
    )
