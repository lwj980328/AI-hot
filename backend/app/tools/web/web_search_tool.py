"""WebSearchTool - Tavily 搜索实现

使用 Tavily Search API 进行网页搜索。
- 需要配置 TAVILY_API_KEY
- 免费额度：1000 次/月
- 返回结构化搜索结果
"""

import logging
import httpx
from pydantic import BaseModel

from app.tools.base.base_tool import BaseTool
from app.tools.web.schemas import WebSearchInput, WebSearchOutput, WebSearchResult
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Tavily API 配置
TAVILY_API_URL = "https://api.tavily.com/search"


class WebSearchTool(BaseTool):
    """网页搜索工具（Tavily 实现）"""

    name = "web_search"
    description = "Search the web using Tavily API"
    version = "1.0.0"
    input_schema = WebSearchInput
    output_schema = WebSearchOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """执行网页搜索（Tavily API）"""
        if not isinstance(input_data, WebSearchInput):
            from app.tools.base import ToolValidationError
            raise ToolValidationError("WebSearchTool 输入类型错误")

        settings = get_settings()
        api_key = settings.tavily_api_key

        # 未配置 API Key 时降级为空结果
        if not api_key:
            logger.warning(
                f"WebSearchTool: TAVILY_API_KEY 未配置，返回空结果。keyword='{input_data.keyword}'"
            )
            return WebSearchOutput(
                query=input_data.keyword,
                results=[],
                placeholder=True,
            )

        # 调用 Tavily API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    TAVILY_API_URL,
                    json={
                        "api_key": api_key,
                        "query": input_data.keyword,
                        "max_results": min(input_data.limit, 10),  # Tavily 最多 10 条
                        "search_depth": "basic",  # basic 或 advanced
                        "include_answer": False,
                        "include_raw_content": False,
                    },
                )
                response.raise_for_status()
                data = response.json()

            # 解析结果
            results = []
            for item in data.get("results", []):
                results.append(
                    WebSearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("content", ""),
                        url=item.get("url", ""),
                    )
                )

            logger.info(
                f"WebSearchTool: Tavily 搜索成功，keyword='{input_data.keyword}', "
                f"results={len(results)}"
            )

            return WebSearchOutput(
                query=input_data.keyword,
                results=results,
                placeholder=False,
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"WebSearchTool: Tavily API HTTP 错误 {e.response.status_code}: {e.response.text}"
            )
            # 降级为空结果
            return WebSearchOutput(
                query=input_data.keyword,
                results=[],
                placeholder=True,
            )

        except Exception as e:
            logger.error(f"WebSearchTool: Tavily 搜索失败: {e}")
            # 降级为空结果
            return WebSearchOutput(
                query=input_data.keyword,
                results=[],
                placeholder=True,
            )
