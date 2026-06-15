"""HuggingFaceTool 输入输出 Schema"""

from pydantic import BaseModel, Field


class HuggingFaceModel(BaseModel):
    """HuggingFace 模型条目"""
    model_id: str = ""
    author: str = ""
    likes: int = 0
    downloads: int = 0
    pipeline_tag: str = ""
    tags: list[str] = Field(default_factory=list)
    url: str = ""


class HuggingFaceSearchInput(BaseModel):
    """HuggingFace 搜索输入"""
    keyword: str
    limit: int = 10
    sort: str = "downloads"  # downloads, likes, lastModified
    direction: str = "-1"  # -1 desc, 1 asc


class HuggingFaceSearchOutput(BaseModel):
    """HuggingFace 搜索输出"""
    query: str = ""
    results: list[HuggingFaceModel] = Field(default_factory=list)
