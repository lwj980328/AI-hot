"""研究记忆 - 保存完整研究结果

用于历史研究复用：当用户再次研究同一主题时，可以召回之前的完整研究报告。
向量化字段：report_summary
对应 Collection：research_memory
"""

from app.memory.models.memory_record import MemoryRecord


class ResearchMemory(MemoryRecord):
    """研究记忆"""

    memory_type: str = "research"
    report_title: str = ""
    report_summary: str = ""
    report_markdown: str = ""
