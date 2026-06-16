"""节点执行日志表

记录每个工作流节点的输入/输出摘要，用于前端展示节点执行详情。
对应设计：与 tool_execution_logs 表结构类似，但记录节点级别的执行信息。
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class NodeExecutionLog(Base):
    """节点执行日志表"""
    __tablename__ = "node_execution_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workflow_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    node_name: Mapped[str] = mapped_column(String(50), nullable=False)
    input_summary: Mapped[str] = mapped_column(Text, default="")
    output_summary: Mapped[str] = mapped_column(Text, default="")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # 关系
    workflow_run: Mapped["WorkflowRun"] = relationship(back_populates="node_logs")
