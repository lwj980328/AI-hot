"""LocalTool 本地工具基类

封装本地工具通用的 HTTP 调用、超时控制、异常转换逻辑。
具体工具（ArxivTool/GithubTool/...）继承此类后只需实现 API 特定的解析。
"""

from abc import ABC
from typing import Any
import httpx
import logging

from app.core.config import get_settings
from app.tools.base.base_tool import BaseTool
from app.tools.base.exceptions import (
    ToolConnectionError,
    ToolTimeoutError,
    ToolAuthenticationError,
    ToolRateLimitError,
)

logger = logging.getLogger(__name__)


class LocalTool(BaseTool, ABC):
    """本地工具基类

    提供统一的异步 HTTP GET/JSON 请求能力。
    """

    async def _get_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """发送 GET 请求并返回 JSON

        Args:
            url: 请求地址
            headers: 请求头
            params: 查询参数

        Returns:
            JSON 解析后的对象

        Raises:
            ToolTimeoutError: 超时
            ToolConnectionError: 连接失败或 HTTP 错误
            ToolAuthenticationError: 401/403
            ToolRateLimitError: 429
        """
        settings = get_settings()
        timeout_seconds = getattr(settings, "tool_timeout_seconds", 30)
        merged_headers = {
            "Accept": "application/json",
            "User-Agent": "AI-Hotspot-Research-Agent/0.1.0",
        }
        if headers:
            merged_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                response = await client.get(url, headers=merged_headers, params=params)

                if response.status_code == 429:
                    raise ToolRateLimitError(f"{self.name} 触发限流: {url}")
                if response.status_code in (401, 403):
                    raise ToolAuthenticationError(
                        f"{self.name} 认证失败 ({response.status_code}): {url}"
                    )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            logger.warning(f"{self.name} 请求超时: {url}")
            raise ToolTimeoutError(f"{self.name} 请求超时: {e}") from e
        except httpx.HTTPStatusError as e:
            logger.warning(f"{self.name} HTTP 错误: {e.response.status_code} - {url}")
            raise ToolConnectionError(
                f"{self.name} HTTP 错误 {e.response.status_code}: {url}"
            ) from e
        except httpx.RequestError as e:
            logger.warning(f"{self.name} 连接失败: {url} - {e}")
            raise ToolConnectionError(f"{self.name} 连接失败: {e}") from e

    async def _get_text(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """发送 GET 请求并返回原始文本（用于 XML/Atom 等）"""
        settings = get_settings()
        timeout_seconds = getattr(settings, "tool_timeout_seconds", 30)
        merged_headers = {
            "User-Agent": "AI-Hotspot-Research-Agent/0.1.0",
        }
        if headers:
            merged_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                response = await client.get(url, headers=merged_headers, params=params)
                response.raise_for_status()
                return response.text

        except httpx.TimeoutException as e:
            logger.warning(f"{self.name} 请求超时: {url}")
            raise ToolTimeoutError(f"{self.name} 请求超时: {e}") from e
        except httpx.HTTPStatusError as e:
            logger.warning(f"{self.name} HTTP 错误: {e.response.status_code} - {url}")
            raise ToolConnectionError(
                f"{self.name} HTTP 错误 {e.response.status_code}: {url}"
            ) from e
        except httpx.RequestError as e:
            logger.warning(f"{self.name} 连接失败: {url} - {e}")
            raise ToolConnectionError(f"{self.name} 连接失败: {e}") from e
