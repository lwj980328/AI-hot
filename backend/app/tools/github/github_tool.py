"""GithubTool - 调用 GitHub Search API 搜索仓库

文档：https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
"""

import logging
from urllib.parse import quote_plus
from pydantic import BaseModel

from app.core.config import get_settings
from app.tools.base import LocalTool
from app.tools.github.schemas import GithubSearchInput, GithubSearchOutput, GithubRepository

logger = logging.getLogger(__name__)


class GithubTool(LocalTool):
    """GitHub 仓库搜索工具"""

    name = "github_search"
    description = "Search repositories on GitHub by keyword"
    version = "0.1.0"
    input_schema = GithubSearchInput
    output_schema = GithubSearchOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """执行 GitHub 仓库搜索"""
        if not isinstance(input_data, GithubSearchInput):
            from app.tools.base import ToolValidationError
            raise ToolValidationError("GithubTool 输入类型错误")

        settings = get_settings()
        token = getattr(settings, "github_api_token", "")

        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        encoded_keyword = quote_plus(input_data.keyword)
        url = (
            "https://api.github.com/search/repositories"
            f"?q={encoded_keyword}"
            f"&sort={input_data.sort}"
            f"&order={input_data.order}"
            f"&per_page={min(input_data.limit, 100)}"
        )

        logger.info(f"GithubTool: 搜索 '{input_data.keyword}', limit={input_data.limit}")
        data = await self._get_json(url, headers=headers)
        return self._parse_response(data, input_data.keyword)

    def _parse_response(self, data: dict, keyword: str) -> GithubSearchOutput:
        """解析 GitHub API 响应"""
        items = data.get("items", []) or []
        repositories = []

        for item in items:
            try:
                repositories.append(self._parse_item(item))
            except Exception as e:
                logger.warning(f"GithubTool: 解析单个仓库失败: {e}")
                continue

        return GithubSearchOutput(
            query=keyword,
            total_count=data.get("total_count", 0),
            results=repositories,
        )

    def _parse_item(self, item: dict) -> GithubRepository:
        """解析单个仓库项"""
        owner = item.get("owner", {}) or {}
        return GithubRepository(
            full_name=item.get("full_name", ""),
            name=item.get("name", ""),
            owner=owner.get("login", ""),
            description=item.get("description", "") or "",
            stars=item.get("stargazers_count", 0),
            forks=item.get("forks_count", 0),
            language=item.get("language", "") or "",
            url=item.get("html_url", ""),
            topics=item.get("topics", []) or [],
        )
