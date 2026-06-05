from pydantic import BaseModel, Field
from app.schemas.records.paper_record import PaperRecord
from app.schemas.records.repository_record import RepositoryRecord
from app.schemas.records.model_record import ModelRecord


class ResearchState(BaseModel):
    """研究任务状态"""
    topic: str = ""
    keywords: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    search_round: int = 0
    need_more_data: bool = False
    information_gaps: list[str] = Field(default_factory=list)

    # 研究结果
    papers: list[PaperRecord] = Field(default_factory=list)
    repositories: list[RepositoryRecord] = Field(default_factory=list)
    models: list[ModelRecord] = Field(default_factory=list)
