"""WebSearchTool 输入输出 Schema"""

from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):
    """网页搜索结果条目"""
    title: str = ""
    snippet: str = ""
    url: str = ""


class WebSearchInput(BaseModel):
    """网页搜索输入"""
    keyword: str
    limit: int = 10


class WebSearchOutput(BaseModel):
    """网页搜索输出"""
    query: str = ""
    results: list[WebSearchResult] = Field(default_factory=list)
    placeholder: bool = False  # 标记是否为占位实现
