"""趋势快照 - 保存某个时间点的趋势状态

用于趋势比较：对比同一主题在不同时间点的数据变化。
向量化字段：summary
对应 Collection：trend_memory
"""

from app.memory.models.memory_record import MemoryRecord


class TrendSnapshot(MemoryRecord):
    """趋势快照"""

    memory_type: str = "trend"
    hot_topics: list[str] = []
    project_count: int = 0
    paper_count: int = 0
    model_count: int = 0
    confidence_score: float = 0.0
