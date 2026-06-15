"""GithubTool 单元测试

Mock GitHub Search API 响应，测试 JSON 解析和输出结构。
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.tools.github import GithubTool
from app.tools.github.schemas import GithubSearchInput, GithubSearchOutput

MOCK_GITHUB_RESPONSE = {
    "total_count": 2,
    "items": [
        {
            "full_name": "modelcontextprotocol/python-sdk",
            "name": "python-sdk",
            "owner": {"login": "modelcontextprotocol"},
            "description": "Official Python SDK for MCP",
            "stargazers_count": 5000,
            "forks_count": 300,
            "language": "Python",
            "html_url": "https://github.com/modelcontextprotocol/python-sdk",
            "topics": ["mcp", "ai"],
        },
        {
            "full_name": "example/mcp-tool",
            "name": "mcp-tool",
            "owner": {"login": "example"},
            "description": "An MCP tool example",
            "stargazers_count": 100,
            "forks_count": 10,
            "language": "TypeScript",
            "html_url": "https://github.com/example/mcp-tool",
            "topics": [],
        },
    ],
}


@pytest.fixture
def github_tool():
    return GithubTool()


@pytest.mark.asyncio
async def test_github_tool_success(github_tool):
    """测试成功解析 GitHub API JSON"""
    with patch.object(github_tool, "_get_json", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MOCK_GITHUB_RESPONSE

        result = await github_tool.execute(GithubSearchInput(keyword="MCP"))

    assert isinstance(result, GithubSearchOutput)
    assert result.query == "MCP"
    assert result.total_count == 2
    assert len(result.results) == 2

    repo = result.results[0]
    assert repo.full_name == "modelcontextprotocol/python-sdk"
    assert repo.stars == 5000
    assert repo.language == "Python"
    assert len(repo.topics) == 2


@pytest.mark.asyncio
async def test_github_tool_empty_results(github_tool):
    """测试空结果"""
    empty_response = {"total_count": 0, "items": []}

    with patch.object(github_tool, "_get_json", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = empty_response

        result = await github_tool.execute(GithubSearchInput(keyword="nonexistent"))

    assert isinstance(result, GithubSearchOutput)
    assert result.total_count == 0
    assert len(result.results) == 0


@pytest.mark.asyncio
async def test_github_tool_missing_fields(github_tool):
    """测试字段缺失时的容错处理"""
    partial_response = {
        "total_count": 1,
        "items": [
            {
                "full_name": "test/repo",
                "name": "repo",
                # owner 缺失
                "stargazers_count": 10,
                # description 缺失
                # language 缺失
                "html_url": "https://github.com/test/repo",
            }
        ],
    }

    with patch.object(github_tool, "_get_json", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = partial_response

        result = await github_tool.execute(GithubSearchInput(keyword="test"))

    repo = result.results[0]
    assert repo.full_name == "test/repo"
    assert repo.description == ""
    assert repo.language == ""
    assert repo.owner == ""
