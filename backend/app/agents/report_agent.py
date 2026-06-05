import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ReportAgent:
    """报告Agent - 负责生成研究报告"""

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """生成研究报告"""
        state.status = TaskStatus.REPORTING

        papers_summary = "\n".join(
            f"- {p.title}: {p.summary}" for p in state.research.papers
        )
        repos_summary = "\n".join(
            f"- {r.title} ({r.stars}⭐): {r.summary}" for r in state.research.repositories
        )

        prompt = f"""你是一位AI研究报告撰写专家。请基于以下研究数据生成一份专业的研究报告。

## 研究主题
{state.research.topic or state.user_query}

## 关键词
{', '.join(state.research.keywords)}

## 研究论文
{papers_summary}

## 相关项目
{repos_summary}

请生成一份Markdown格式的研究报告，包含以下部分：
1. 标题
2. 执行摘要（100字以内）
3. 研究背景
4. 核心发现
5. 技术趋势分析
6. 代表性项目/论文介绍
7. 未来展望

请返回JSON格式：
{{
    "title": "报告标题",
    "summary": "执行摘要",
    "markdown_content": "完整的Markdown报告内容"
}}"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.report.title = data.get("title", f"{state.research.topic}研究报告")
            state.report.summary = data.get("summary", "")
            state.report.markdown_content = data.get("markdown_content", "")

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认报告: {e}")
            topic = state.research.topic or state.user_query
            state.report.title = f"{topic}研究报告"
            state.report.summary = f"本报告对{topic}进行了研究分析"
            state.report.markdown_content = self._generate_default_report(state)

        state.status = TaskStatus.COMPLETED
        return state

    def _generate_default_report(self, state: AgentState) -> str:
        """生成默认报告（LLM调用失败时使用）"""
        topic = state.research.topic or state.user_query
        papers_section = "\n".join(
            f"### {p.title}\n{p.summary}\n" for p in state.research.papers
        )
        repos_section = "\n".join(
            f"### {r.title}\n{r.summary}\nStars: {r.stars}\n" for r in state.research.repositories
        )

        return f"""# {topic}研究报告

## 执行摘要

本报告对{topic}领域的最新发展进行了研究分析，涵盖了相关论文和开源项目。

## 研究背景

{topic}是当前AI领域的研究热点之一，受到了学术界和工业界的广泛关注。

## 代表性论文

{papers_section}

## 相关开源项目

{repos_section}

## 未来展望

{topic}领域仍有广阔的发展空间，值得持续关注和深入研究。

---
*报告生成时间: 本报告由AI Research OS自动生成*
"""
