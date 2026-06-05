import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Task(Base):
    """研究任务表"""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_query: Mapped[str] = mapped_column(String(1000), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), default="research")
    status: Mapped[str] = mapped_column(String(50), default="created")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    workflow_runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="task")
    report: Mapped["Report | None"] = relationship(back_populates="task")
