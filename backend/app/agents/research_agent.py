import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.schemas.records.paper_record import PaperRecord
from app.schemas.records.repository_record import RepositoryRecord
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ResearchAgent:
    """研究Agent - 负责资料采集

    M1阶段：通过LLM模拟生成研究数据
    M4阶段：接入ToolRegistry调用真实工具
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """执行研究任务"""
        state.status = TaskStatus.RESEARCHING
        topic = state.research.topic or state.user_query

        prompt = f"""你是一位AI研究助手。请针对主题"{topic}"生成模拟的研究数据。

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
4. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.research.keywords = data.get("keywords", [topic])
            state.research.papers = [
                PaperRecord(
                    title=p["title"],
                    authors=p.get("authors", []),
                    summary=p.get("summary", ""),
                    url=p.get("url", ""),
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
                )
                for r in data.get("repositories", [])
            ]

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认数据: {e}")
            state.research.keywords = [topic]
            state.research.papers = [
                PaperRecord(
                    title=f"{topic}研究综述",
                    authors=["AI Researcher"],
                    summary=f"关于{topic}的最新研究进展",
                    url="https://arxiv.org/abs/2024.00001",
                )
            ]
            state.research.repositories = [
                RepositoryRecord(
                    title=f"{topic.lower().replace(' ', '-')}-toolkit",
                    stars=500,
                    language="Python",
                    summary=f"{topic}相关工具库",
                    url="https://github.com/example/repo",
                )
            ]

        return state
