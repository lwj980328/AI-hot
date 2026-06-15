"""ArxivTool 输入输出 Schema"""

from datetime import datetime
from pydantic import BaseModel, Field


class ArxivPaper(BaseModel):
    """Arxiv 论文条目"""
    title: str = ""
    summary: str = ""
    authors: list[str] = Field(default_factory=list)
    arxiv_id: str = ""
    published_at: datetime = Field(default_factory=datetime.now)
    url: str = ""
    primary_category: str = ""


class ArxivSearchInput(BaseModel):
    """Arxiv 搜索输入"""
    keyword: str
    limit: int = 10


class ArxivSearchOutput(BaseModel):
    """Arxiv 搜索输出"""
    query: str = ""
    total_results: int = 0
    results: list[ArxivPaper] = Field(default_factory=list)
