"""统一记忆基类

所有记忆类型（ResearchMemory、TrendSnapshot、InsightMemory）都继承此基类。
定义了记忆的通用字段：ID、类型、主题、摘要、来源、时间戳。
"""

from datetime import datetime
from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """统一记忆基类"""

    memory_id: str = ""
    memory_type: str = ""  # research | trend | insight
    topic: str = ""
    summary: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
