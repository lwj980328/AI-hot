import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.services.llm_service import LLMService
from app.tools.base.tool_service import ToolService

logger = logging.getLogger(__name__)

# 工具名称 → 数据源标识映射
TOOL_TO_SOURCE = {
    "arxiv_search": "arxiv",
    "github_search": "github",
    "huggingface_search": "huggingface",
    "web_search": "web",
}

# 数据源描述（用于构建 prompt）
SOURCE_DESCRIPTIONS = {
    "arxiv": "学术论文（arxiv.org）",
    "github": "开源项目（GitHub）",
    "huggingface": "AI 模型（HuggingFace）",
    "web": "网络资讯和博客",
}


class PlannerAgent:
    """规划Agent - 将用户需求转换为研究计划

    职责：
    - 读取 user_query
    - 输出 research.topic, research.keywords, research.data_sources

    约束：
    - 禁止调用任何 Tool
    - 禁止修改 context / analysis / memory / report
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        tool_service: ToolService | None = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.tool_service = tool_service or ToolService()

    async def run(self, state: AgentState) -> AgentState:
        """执行研究规划"""
        state.status = TaskStatus.PLANNING

        # 动态获取可用数据源
        available_sources = self._get_available_sources()
        sources_desc = self._build_sources_description(available_sources)

        prompt = f"""你是一位AI研究规划专家。请根据用户的查询，制定一份结构化的研究计划。

## 用户查询
{state.user_query}

## 可用数据源
{sources_desc}

请返回JSON格式：
{{
    "topic": "研究主题（简短，如：MCP生态）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "data_sources": {available_sources}
}}

要求：
1. topic 应该是对用户查询的精炼概括
2. keywords 应包含中英文关键词，用于后续检索
3. data_sources 从上述可用数据源中选择最相关的
4. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.research.topic = data.get("topic", state.user_query)
            state.research.keywords = data.get("keywords", [state.user_query])
            # 过滤掉不可用的数据源
            requested_sources = data.get("data_sources", available_sources[:2])
            state.research.data_sources = [
                s for s in requested_sources if s in available_sources
            ] or available_sources[:2]

            logger.info(
                f"PlannerAgent: topic={state.research.topic}, "
                f"keywords={state.research.keywords}, "
                f"data_sources={state.research.data_sources}"
            )

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认规划: {e}")
            state.research.topic = state.user_query
            state.research.keywords = [state.user_query]
            state.research.data_sources = available_sources[:2]

        return state

    def _get_available_sources(self) -> list[str]:
        """从 ToolRegistry 获取可用数据源列表"""
        available = []
        tools = self.tool_service.list_available_tools()
        for tool_meta in tools:
            tool_name = tool_meta.get("name", "")
            source = TOOL_TO_SOURCE.get(tool_name)
            if source:
                available.append(source)
        return available

    @staticmethod
    def _build_sources_description(sources: list[str]) -> str:
        """构建数据源描述文本"""
        lines = []
        for source in sources:
            desc = SOURCE_DESCRIPTIONS.get(source, source)
            lines.append(f"- {source}: {desc}")
        return "\n".join(lines)
