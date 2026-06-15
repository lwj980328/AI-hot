"""ArxivTool 单元测试

Mock arxiv.org API 响应，测试 Atom XML 解析和输出结构。
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.tools.arxiv import ArxivTool
from app.tools.arxiv.schemas import ArxivSearchInput, ArxivSearchOutput

MOCK_ATOM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <title>ArXiv Query</title>
  <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">2</totalResults>
  <entry>
    <id>http://arxiv.org/abs/2401.12345v1</id>
    <title>Test Paper About MCP</title>
    <summary>This is a test summary about MCP.</summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <published>2024-01-15T00:00:00Z</published>
    <arxiv:primary_category term="cs.AI" />
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.67890v1</id>
    <title>Another Paper About Agents</title>
    <summary>Summary about AI agents.</summary>
    <author><name>Charlie Brown</name></author>
    <published>2024-01-20T00:00:00Z</published>
    <arxiv:primary_category term="cs.CL" />
  </entry>
</feed>"""


@pytest.fixture
def arxiv_tool():
    return ArxivTool()


@pytest.mark.asyncio
async def test_arxiv_tool_success(arxiv_tool):
    """测试成功解析 Arxiv Atom XML"""
    with patch.object(arxiv_tool, "_get_text", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MOCK_ATOM_XML

        result = await arxiv_tool.execute(ArxivSearchInput(keyword="MCP"))

    assert isinstance(result, ArxivSearchOutput)
    assert result.query == "MCP"
    assert result.total_results == 2
    assert len(result.results) == 2

    paper = result.results[0]
    assert paper.title == "Test Paper About MCP"
    assert paper.arxiv_id == "2401.12345v1"
    assert len(paper.authors) == 2
    assert "Alice Smith" in paper.authors
    assert paper.primary_category == "cs.AI"


@pytest.mark.asyncio
async def test_arxiv_tool_empty_results(arxiv_tool):
    """测试空结果"""
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>ArXiv Query</title>
  <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">0</totalResults>
</feed>"""

    with patch.object(arxiv_tool, "_get_text", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = empty_xml

        result = await arxiv_tool.execute(ArxivSearchInput(keyword="nonexistent"))

    assert isinstance(result, ArxivSearchOutput)
    assert result.total_results == 0
    assert len(result.results) == 0
