import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class PlannerAgent:
    """规划Agent - 将用户需求转换为研究计划

    职责：
    - 读取 user_query
    - 输出 research.topic, research.keywords, research.data_sources

    约束：
    - 禁止调用任何 Tool
    - 禁止修改 context / analysis / memory / report
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """执行研究规划"""
        state.status = TaskStatus.PLANNING

        prompt = f"""你是一位AI研究规划专家。请根据用户的查询，制定一份结构化的研究计划。

## 用户查询
{state.user_query}

请返回JSON格式：
{{
    "topic": "研究主题（简短，如：MCP生态）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "data_sources": ["arxiv", "github", "huggingface"]
}}

要求：
1. topic 应该是对用户查询的精炼概括
2. keywords 应包含中英文关键词，用于后续检索
3. data_sources 从 arxiv、github、huggingface 中选择最相关的
4. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.research.topic = data.get("topic", state.user_query)
            state.research.keywords = data.get("keywords", [state.user_query])
            state.research.data_sources = data.get("data_sources", ["arxiv", "github"])

            logger.info(
                f"PlannerAgent: topic={state.research.topic}, "
                f"keywords={state.research.keywords}"
            )

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认规划: {e}")
            state.research.topic = state.user_query
            state.research.keywords = [state.user_query]
            state.research.data_sources = ["arxiv", "github"]

        return state
