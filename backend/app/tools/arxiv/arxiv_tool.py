"""ArxivTool - 调用 arxiv.org API 搜索论文

使用 arxiv.org 的 Atom API，无需认证。
API 文档：https://arxiv.org/help/api/user-manual
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus
from pydantic import BaseModel

from app.core.config import get_settings
from app.tools.base import LocalTool
from app.tools.arxiv.schemas import ArxivSearchInput, ArxivSearchOutput, ArxivPaper

logger = logging.getLogger(__name__)

# Atom namespace
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_NS = {"arxiv": "http://arxiv.org/schemas/atom"}
# OpenSearch namespace（用于解析 totalResults）
OS_NS = {"os": "http://a9.com/-/spec/opensearch/1.1/"}


class ArxivTool(LocalTool):
    """Arxiv 论文搜索工具"""

    name = "arxiv_search"
    description = "Search papers on arxiv.org by keyword"
    version = "0.1.0"
    input_schema = ArxivSearchInput
    output_schema = ArxivSearchOutput

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """执行 Arxiv 搜索"""
        if not isinstance(input_data, ArxivSearchInput):
            from app.tools.base import ToolValidationError
            raise ToolValidationError("ArxivTool 输入类型错误")

        settings = get_settings()
        max_results = getattr(settings, "arxiv_max_results", 10)
        limit = min(input_data.limit, max_results)

        query = quote_plus(input_data.keyword)
        url = (
            "http://export.arxiv.org/api/query"
            f"?search_query=all:{query}"
            f"&start=0"
            f"&max_results={limit}"
            f"&sortBy=submittedDate"
            f"&sortOrder=descending"
        )

        logger.info(f"ArxivTool: 搜索 '{input_data.keyword}', limit={limit}")
        xml_text = await self._get_text(url)
        return self._parse_atom(xml_text, input_data.keyword)

    def _parse_atom(self, xml_text: str, keyword: str) -> ArxivSearchOutput:
        """解析 Arxiv Atom XML"""
        root = ET.fromstring(xml_text.encode("utf-8"))

        total_results = 0
        total_elem = root.find("os:totalResults", OS_NS)
        if total_elem is not None and total_elem.text:
            total_results = int(total_elem.text)

        papers = []
        for entry in root.findall("atom:entry", ATOM_NS):
            try:
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)
            except Exception as e:
                logger.warning(f"ArxivTool: 解析单条论文失败: {e}")
                continue

        return ArxivSearchOutput(
            query=keyword,
            total_results=total_results,
            results=papers,
        )

    def _parse_entry(self, entry: ET.Element) -> ArxivPaper | None:
        """解析单个 Atom entry"""
        title_elem = entry.find("atom:title", ATOM_NS)
        summary_elem = entry.find("atom:summary", ATOM_NS)
        id_elem = entry.find("atom:id", ATOM_NS)
        published_elem = entry.find("atom:published", ATOM_NS)

        if title_elem is None or id_elem is None:
            return None

        title = self._clean_text(title_elem.text or "")
        summary = self._clean_text(summary_elem.text or "") if summary_elem is not None else ""
        arxiv_url = id_elem.text or ""

        # arxiv_id 从 URL 提取，例如 http://arxiv.org/abs/2401.12345v1
        arxiv_id = arxiv_url.split("/")[-1] if arxiv_url else ""

        # 发布时间
        published_at = datetime.now()
        if published_elem is not None and published_elem.text:
            try:
                published_at = datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
            except Exception:
                pass

        # 作者
        authors = []
        for author_elem in entry.findall("atom:author", ATOM_NS):
            name_elem = author_elem.find("atom:name", ATOM_NS)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())

        # 主分类
        primary_category = ""
        cat_elem = entry.find("arxiv:primary_category", ARXIV_NS)
        if cat_elem is not None:
            primary_category = cat_elem.get("term", "")

        return ArxivPaper(
            title=title,
            summary=summary,
            authors=authors,
            arxiv_id=arxiv_id,
            published_at=published_at,
            url=arxiv_url,
            primary_category=primary_category,
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        """清理文本中的多余空白和换行"""
        return " ".join(text.split())
