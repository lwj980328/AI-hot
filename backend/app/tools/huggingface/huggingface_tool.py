"""HuggingFaceTool - 调用 HuggingFace Hub API 搜索模型

API 文档：https://huggingface.co/docs/hub/api#get-apimodels
"""

import logging
from urllib.parse import quote_plus
from pydantic import BaseModel

from app.core.config import get_settings
from app.tools.base import LocalTool
from app.tools.huggingface.schemas import (
    HuggingFaceSearchInput,
    HuggingFaceSearchOutput,
    HuggingFaceModel,
)

logger = logging.getLogger(__name__)


class HuggingFaceTool(LocalTool):
    """HuggingFace 模型搜索工具"""

    name = "huggingface_search"
    description = "Search models on HuggingFace Hub by keyword"
    version = "0.1.0"
    input_schema = HuggingFaceSearchInput
    output_schema = HuggingFaceSearchOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """执行 HuggingFace 模型搜索"""
        if not isinstance(input_data, HuggingFaceSearchInput):
            from app.tools.base import ToolValidationError
            raise ToolValidationError("HuggingFaceTool 输入类型错误")

        settings = get_settings()
        max_results = getattr(settings, "huggingface_max_results", 10)
        limit = min(input_data.limit, max_results)

        url = "https://huggingface.co/api/models"
        params = {
            "search": quote_plus(input_data.keyword),
            "limit": limit,
            "sort": input_data.sort,
            "direction": input_data.direction,
        }

        logger.info(f"HuggingFaceTool: 搜索 '{input_data.keyword}', limit={limit}")
        data = await self._get_json(url, params=params)
        return self._parse_response(data, input_data.keyword)

    def _parse_response(self, data: list, keyword: str) -> HuggingFaceSearchOutput:
        """解析 HuggingFace API 响应

        注意：HuggingFace API 返回的是数组而非对象。
        """
        models = []
        for item in data:
            try:
                models.append(self._parse_item(item))
            except Exception as e:
                logger.warning(f"HuggingFaceTool: 解析单个模型失败: {e}")
                continue

        return HuggingFaceSearchOutput(
            query=keyword,
            results=models,
        )

    def _parse_item(self, item: dict) -> HuggingFaceModel:
        """解析单个模型项"""
        model_id = item.get("id", item.get("modelId", ""))
        author = item.get("author", "")
        if not author and "/" in model_id:
            author = model_id.split("/")[0]

        return HuggingFaceModel(
            model_id=model_id,
            author=author,
            likes=item.get("likes", 0),
            downloads=item.get("downloads", 0),
            pipeline_tag=item.get("pipeline_tag", "") or "",
            tags=item.get("tags", []) or [],
            url=f"https://huggingface.co/{model_id}",
        )
