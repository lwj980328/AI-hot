"""WebSearchTool - 占位实现

当前为占位实现，注册到 Registry 但返回空结果。
未来可接入 Serper / Bing 等外部搜索 API。
"""

import logging
from pydantic import BaseModel

from app.tools.base.base_tool import BaseTool
from app.tools.web.schemas import WebSearchInput, WebSearchOutput

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """网页搜索工具（占位实现）"""

    name = "web_search"
    description = "Search the web (placeholder - returns empty results)"
    version = "0.1.0"
    input_schema = WebSearchInput
    output_schema = WebSearchOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """执行网页搜索（占位：返回空结果）"""
        if not isinstance(input_data, WebSearchInput):
            from app.tools.base import ToolValidationError
            raise ToolValidationError("WebSearchTool 输入类型错误")

        logger.warning(
            f"WebSearchTool: 占位实现，返回空结果。keyword='{input_data.keyword}'"
        )
        return WebSearchOutput(
            query=input_data.keyword,
            results=[],
            placeholder=True,
        )
