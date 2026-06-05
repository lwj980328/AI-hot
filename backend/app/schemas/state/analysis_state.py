from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """证据"""
    evidence_id: str = ""
    statement: str = ""
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class AnalysisInsight(BaseModel):
    """分析洞察"""
    title: str = ""
    description: str = ""
    evidences: list[Evidence] = Field(default_factory=list)


class AnalysisState(BaseModel):
    """分析状态"""
    hot_topics: list[str] = Field(default_factory=list)
    trend_summary: str = ""
    insights: list[AnalysisInsight] = Field(default_factory=list)
