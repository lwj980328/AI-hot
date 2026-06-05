from datetime import datetime
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    """统一文档基类"""
    source_id: str = ""
    source_type: str = ""  # paper | repository | model
    title: str = ""
    summary: str = ""
    url: str = ""
    collected_at: datetime = Field(default_factory=datetime.now)
