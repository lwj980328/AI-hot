"""记忆 API 响应模型

遵循 docs/08_API设计.md 规范，使用 Pydantic 强类型定义。
"""

from datetime import datetime
from pydantic import BaseModel, Field


class MemoryEvidenceResponse(BaseModel):
    """记忆证据响应"""

    statement: str = Field(description="证据陈述")
    source_ids: list[str] = Field(default_factory=list, description="来源 ID 列表")
    confidence: float = Field(description="置信度")


class MemoryItemResponse(BaseModel):
    """单条记忆响应"""

    memory_id: str = Field(description="记忆 ID")
    memory_type: str = Field(description="记忆类型: research | trend | insight")
    topic: str = Field(description="主题")
    summary: str = Field(description="摘要")
    created_at: datetime | None = Field(default=None, description="创建时间")
    source_ids: list[str] = Field(default_factory=list, description="来源 ID 列表")
    score: float = Field(default=0.0, description="相似度分数（搜索时有值）")

    # Research Memory 特有字段
    report_title: str | None = Field(default=None, description="报告标题")
    report_summary: str | None = Field(default=None, description="报告摘要")

    # Trend Snapshot 特有字段
    hot_topics: list[str] | None = Field(default=None, description="热门话题")
    project_count: int | None = Field(default=None, description="项目数")
    paper_count: int | None = Field(default=None, description="论文数")
    model_count: int | None = Field(default=None, description="模型数")
    confidence_score: float | None = Field(default=None, description="置信度分数")

    # Insight Memory 特有字段
    insight_title: str | None = Field(default=None, description="洞察标题")
    insight_description: str | None = Field(default=None, description="洞察描述")
    evidences: list[MemoryEvidenceResponse] | None = Field(
        default=None, description="证据列表"
    )


class MemorySearchResponse(BaseModel):
    """记忆搜索响应"""

    research: list[MemoryItemResponse] = Field(
        default_factory=list, description="研究记忆"
    )
    trend: list[MemoryItemResponse] = Field(
        default_factory=list, description="趋势快照"
    )
    insight: list[MemoryItemResponse] = Field(
        default_factory=list, description="洞察记忆"
    )
    total: int = Field(description="总数量")


class MemoryStatsResponse(BaseModel):
    """记忆统计响应"""

    research_count: int = Field(description="研究记忆数量")
    trend_count: int = Field(description="趋势快照数量")
    insight_count: int = Field(description="洞察记忆数量")
    total: int = Field(description="总数量")
