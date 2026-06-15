"""GithubTool 输入输出 Schema"""

from pydantic import BaseModel, Field


class GithubRepository(BaseModel):
    """GitHub 仓库条目"""
    full_name: str = ""
    name: str = ""
    owner: str = ""
    description: str = ""
    stars: int = 0
    forks: int = 0
    language: str = ""
    url: str = ""
    topics: list[str] = Field(default_factory=list)


class GithubSearchInput(BaseModel):
    """GitHub 搜索输入"""
    keyword: str
    limit: int = 10
    sort: str = "stars"  # stars, forks, updated
    order: str = "desc"  # asc, desc


class GithubSearchOutput(BaseModel):
    """GitHub 搜索输出"""
    query: str = ""
    total_count: int = 0
    results: list[GithubRepository] = Field(default_factory=list)
