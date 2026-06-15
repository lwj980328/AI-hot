"""工具层 - 统一暴露

所有工具通过 ToolRegistry 注册，Agent 通过 ToolService 调用。
"""

from app.tools.base import (
    BaseTool,
    LocalTool,
    ToolRegistry,
    get_tool_registry,
    ToolService,
    get_tool_service,
    ToolError,
    ToolTimeoutError,
    ToolConnectionError,
    ToolValidationError,
    ToolAuthenticationError,
    ToolRateLimitError,
    ToolNotFoundError,
)
from app.tools.arxiv import ArxivTool
from app.tools.github import GithubTool
from app.tools.web import WebSearchTool
from app.tools.huggingface import HuggingFaceTool

__all__ = [
    # Base
    "BaseTool",
    "LocalTool",
    "ToolRegistry",
    "get_tool_registry",
    "ToolService",
    "get_tool_service",
    # Exceptions
    "ToolError",
    "ToolTimeoutError",
    "ToolConnectionError",
    "ToolValidationError",
    "ToolAuthenticationError",
    "ToolRateLimitError",
    "ToolNotFoundError",
    # Tools
    "ArxivTool",
    "GithubTool",
    "WebSearchTool",
    "HuggingFaceTool",
]
