"""洞察记忆 - 保存经过证据验证的高价值洞察

用于跨任务知识复用：不同研究任务之间共享已验证的洞察。
向量化字段：insight_description
对应 Collection：insight_memory
污染控制：confidence < 0.6 或无 source_ids 的洞察不保存
"""

from pydantic import BaseModel, Field
from app.memory.models.memory_record import MemoryRecord


class MemoryEvidence(BaseModel):
    """记忆证据"""

    statement: str = ""
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class InsightMemory(MemoryRecord):
    """洞察记忆"""

    memory_type: str = "insight"
    insight_title: str = ""
    insight_description: str = ""
    evidences: list[MemoryEvidence] = Field(default_factory=list)
