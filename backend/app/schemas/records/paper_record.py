from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.records.source_document import SourceDocument


class PaperRecord(SourceDocument):
    """论文记录"""
    source_type: str = "paper"
    authors: list[str] = Field(default_factory=list)
    published_at: datetime = Field(default_factory=datetime.now)
