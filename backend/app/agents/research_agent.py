"""研究Agent - 负责资料采集

职责：
- 读取 state.research 和 state.context
- 输出 state.research.papers, state.research.repositories, state.research.models
- Deep Research 时读取 information_gaps 执行补充研究

M4改造：接入 ToolService 调用真实工具（Arxiv/GitHub/HuggingFace），
失败时降级到 LLM 模拟数据，并在 data_source_tags 中标记数据来源。

M8重构：移除对 state.tool_calls 的直接操作，
工具调用记录通过 _tool_calls_data 属性传递给节点函数，
由节点函数负责保存到独立的 tool_execution_logs 表。
"""

import logging
from datetime import datetime
from pydantic import BaseModel
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.schemas.records.paper_record import PaperRecord
from app.schemas.records.repository_record import RepositoryRecord
from app.schemas.records.model_record import ModelRecord
from app.services.llm_service import LLMService
from app.tools.base.tool_service import ToolService

logger = logging.getLogger(__name__)

# 工具名称 → data_source 标识映射
TOOL_NAME_MAP = {
    "arxiv": "arxiv_search",
    "github": "github_search",
    "huggingface": "huggingface_search",
    "web": "web_search",
}


class ResearchAgent:
    """研究Agent - 负责资料采集

    职责：
    - 读取 state.research 和 state.context
    - 输出 state.research.papers, state.research.repositories, state.research.models
    - Deep Research 时读取 information_gaps 执行补充研究
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_service: ToolService | None = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.tool_service = tool_service or ToolService()

    async def run(self, state: AgentState) -> AgentState:
        """执行研究任务

        1. 遍历 data_sources，按数据源调用工具
        2. 工具失败时降级到 LLM 模拟数据
        3. 在 data_source_tags 中标记每个数据源的真实/模拟状态
        4. 收集工具调用记录，通过 _tool_calls_data 属性传递
        """
        state.status = TaskStatus.RESEARCHING
        state.research.search_round += 1

        topic = state.research.topic or state.user_query
        keywords = state.research.keywords or [topic]
        data_sources = state.research.data_sources or ["arxiv", "github"]

        # 构建查询关键词（优先用 keywords[0]，附带 gaps 补充信息）
        query_keyword = keywords[0] if keywords else topic
        if state.research.information_gaps:
            query_keyword += " " + " ".join(state.research.information_gaps[:2])

        source_tags: list[str] = []
        tool_calls_data: list[dict] = []  # 收集工具调用记录

        # ============================================================
        # 第一步：按 data_sources 调用真实工具
        # ============================================================
        for source in data_sources:
            tool_name = TOOL_NAME_MAP.get(source)
            if not tool_name:
                logger.warning(f"ResearchAgent: 未知数据源 '{source}'，跳过")
                continue

            try:
                result, call_record = await self._invoke_tool(tool_name, query_keyword)

                # 将工具输出追加到 state.research
                self._merge_tool_result(state, tool_name, result)
                source_tags.append("real")

                # 收集工具调用记录
                tool_calls_data.append(call_record)

                logger.info(f"ResearchAgent: {tool_name} 获取数据成功")

            except Exception as e:
                logger.warning(f"ResearchAgent: {tool_name} 调用失败，降级到 LLM 模拟: {e}")
                source_tags.append("simulated")

        # ============================================================
        # 第二步：如果没有获取到任何真实数据，使用 LLM 模拟全部
        # ============================================================
        real_count = sum(1 for t in source_tags if t == "real")
        if real_count == 0:
            logger.info("ResearchAgent: 所有工具均失败，全面降级到 LLM 模拟数据")
            await self._fallback_llm_generate(state, topic, query_keyword)
            source_tags = ["simulated"] * len(data_sources)

        # 标记数据来源
        state.research.data_source_tags = source_tags

        # 将工具调用记录附加到 state 上，供节点函数读取
        # 注意：这不是 AgentState 的正式字段，只是一个临时传递机制
        state._tool_calls_data = tool_calls_data

        return state

    async def _invoke_tool(self, tool_name: str, keyword: str) -> tuple[BaseModel, dict]:
        """调用指定工具，返回 (结果, 调用记录)"""
        start_time = datetime.now()
        input_params = {"keyword": keyword}

        try:
            if tool_name == "arxiv_search":
                from app.tools.arxiv.schemas import ArxivSearchInput
                result = await self.tool_service.execute(
                    tool_name, ArxivSearchInput(keyword=keyword)
                )
            elif tool_name == "github_search":
                from app.tools.github.schemas import GithubSearchInput
                result = await self.tool_service.execute(
                    tool_name, GithubSearchInput(keyword=keyword)
                )
            elif tool_name == "huggingface_search":
                from app.tools.huggingface.schemas import HuggingFaceSearchInput
                result = await self.tool_service.execute(
                    tool_name, HuggingFaceSearchInput(keyword=keyword)
                )
            elif tool_name == "web_search":
                from app.tools.web.schemas import WebSearchInput
                result = await self.tool_service.execute(
                    tool_name, WebSearchInput(keyword=keyword)
                )
            else:
                raise ValueError(f"未实现的工具: {tool_name}")

            # 计算耗时
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # 构建输出摘要
            result_count = len(result.results) if hasattr(result, "results") else 0
            output_summary = f"获取 {result_count} 条结果"

            # 构建调用记录
            call_record = {
                "node_name": "research",
                "tool_name": tool_name,
                "input_params": input_params,
                "output_summary": output_summary,
                "success": True,
                "duration_ms": duration_ms,
                "called_at": start_time.isoformat(),
            }

            return result, call_record

        except Exception as e:
            # 记录失败的工具调用
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            call_record = {
                "node_name": "research",
                "tool_name": tool_name,
                "input_params": input_params,
                "output_summary": f"调用失败: {str(e)}",
                "success": False,
                "duration_ms": duration_ms,
                "called_at": start_time.isoformat(),
            }
            raise

    def _merge_tool_result(self, state: AgentState, tool_name: str, result: BaseModel) -> None:
        """将工具输出转换并追加到 state.research"""
        now = datetime.now()

        if tool_name == "arxiv_search" and hasattr(result, "results"):
            for paper in result.results:
                state.research.papers.append(PaperRecord(
                    source_id=paper.arxiv_id,
                    source_type="paper",
                    title=paper.title,
                    summary=paper.summary[:200] if paper.summary else "",
                    url=paper.url,
                    authors=paper.authors,
                    published_at=paper.published_at,
                    collected_at=now,
                ))

        elif tool_name == "github_search" and hasattr(result, "results"):
            for repo in result.results:
                state.research.repositories.append(RepositoryRecord(
                    source_id=repo.full_name,
                    source_type="repository",
                    title=repo.full_name,
                    summary=(repo.description[:200] if repo.description else ""),
                    url=repo.url,
                    stars=repo.stars,
                    language=repo.language,
                    collected_at=now,
                ))

        elif tool_name == "huggingface_search" and hasattr(result, "results"):
            for model in result.results:
                state.research.models.append(ModelRecord(
                    source_id=model.model_id,
                    source_type="model",
                    title=model.model_id,
                    summary=f"pipeline: {model.pipeline_tag}, downloads: {model.downloads}",
                    url=model.url,
                    downloads=model.downloads,
                    likes=model.likes,
                    collected_at=now,
                ))

        elif tool_name == "web_search":
            # 占位实现，不追加数据
            pass

    async def _fallback_llm_generate(
        self,
        state: AgentState,
        topic: str,
        keyword: str,
    ) -> None:
        """降级方案：通过 LLM 生成模拟数据

        当所有工具均失败时使用，确保 workflow 不中断。
        """
        # 构建上下文摘要
        context_summary = "\n".join(
            f"- [{c.item_type}] {c.title}: {c.content}"
            for c in state.context.context_items
        ) if state.context.context_items else "无"

        # Deep Research：如果有信息缺口，针对性补充
        gaps_summary = ""
        if state.research.information_gaps:
            gaps_summary = "\n\n## 需要重点补充的信息\n" + "\n".join(
                f"- {gap}" for gap in state.research.information_gaps
            )

        prompt = f"""你是一位AI研究助手。请针对主题"{topic}"生成模拟的研究数据。

## 上下文信息
{context_summary}
{gaps_summary}

请返回JSON格式，包含以下内容：
{{
    "papers": [
        {{
            "title": "论文标题",
            "authors": ["作者1", "作者2"],
            "summary": "论文摘要（50字以内）",
            "url": "https://arxiv.org/abs/xxxx.xxxxx"
        }}
    ],
    "repositories": [
        {{
            "title": "仓库名称",
            "stars": 1000,
            "language": "Python",
            "summary": "仓库描述（50字以内）",
            "url": "https://github.com/xxx/xxx"
        }}
    ],
    "keywords": ["关键词1", "关键词2"]
}}

要求：
1. 生成3篇论文
2. 生成3个代码仓库
3. 内容要符合主题，看起来真实可信
4. 如果有"需要重点补充的信息"，请针对性生成相关数据
5. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.research.keywords = data.get("keywords", [keyword])
            state.research.papers = [
                PaperRecord(
                    title=p["title"],
                    authors=p.get("authors", []),
                    summary=p.get("summary", ""),
                    url=p.get("url", ""),
                    source_type="paper",
                )
                for p in data.get("papers", [])
            ]
            state.research.repositories = [
                RepositoryRecord(
                    title=r["title"],
                    stars=r.get("stars", 0),
                    language=r.get("language", ""),
                    summary=r.get("summary", ""),
                    url=r.get("url", ""),
                    source_type="repository",
                )
                for r in data.get("repositories", [])
            ]

        except Exception as e:
            logger.warning(f"LLM模拟也失败，使用硬编码默认数据: {e}")
            state.research.keywords = [keyword]
            state.research.papers = [
                PaperRecord(
                    title=f"{topic}研究综述",
                    authors=["AI Researcher"],
                    summary=f"关于{topic}的最新研究进展",
                    url="https://arxiv.org/abs/2024.00001",
                    source_type="paper",
                )
            ]
            state.research.repositories = [
                RepositoryRecord(
                    title=f"{topic.lower().replace(' ', '-')}-toolkit",
                    stars=500,
                    language="Python",
                    summary=f"{topic}相关工具库",
                    url="https://github.com/example/repo",
                    source_type="repository",
                )
            ]
