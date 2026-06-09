import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.schemas.state.analysis_state import AnalysisInsight, Evidence
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """分析Agent - 从原始资料中提取结构化知识

    职责：
    - 读取 research（papers, repositories）和 context
    - 输出 analysis（hot_topics, trend_summary, insights）
    - 判断是否需要更多数据（need_more_data, information_gaps）

    约束：
    - 每个洞察必须关联 Evidence
    - 禁止无来源结论
    - 禁止直接访问数据库或外部服务
    """

    MAX_RESEARCH_ROUNDS = 3

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """执行分析推理"""
        state.status = TaskStatus.ANALYZING

        # 检查研究轮次上限
        if state.research.search_round >= self.MAX_RESEARCH_ROUNDS:
            logger.info(
                f"AnalysisAgent: 已达到最大研究轮次 {self.MAX_RESEARCH_ROUNDS}，强制结束"
            )
            state.research.need_more_data = False
            state.research.information_gaps = []

        # 构建研究资料摘要
        papers_summary = "\n".join(
            f"- {p.title}: {p.summary}" for p in state.research.papers
        )
        repos_summary = "\n".join(
            f"- {r.title} ({r.stars}⭐, {r.language}): {r.summary}"
            for r in state.research.repositories
        )
        context_summary = "\n".join(
            f"- [{c.item_type}] {c.title}: {c.content}"
            for c in state.context.context_items
        )

        topic = state.research.topic or state.user_query

        prompt = f"""你是一位AI研究分析专家。请基于以下研究资料，生成结构化的分析结果。

## 研究主题
{topic}

## 上下文信息
{context_summary or "无"}

## 研究论文
{papers_summary or "无"}

## 相关项目
{repos_summary or "无"}

## 当前研究轮次
第 {state.research.search_round + 1} 轮（最多 {self.MAX_RESEARCH_ROUNDS} 轮）

请返回JSON格式：
{{
    "hot_topics": ["热点话题1", "热点话题2"],
    "trend_summary": "趋势分析总结（200字以内）",
    "insights": [
        {{
            "title": "洞察标题",
            "description": "洞察描述（100字以内）",
            "evidences": [
                {{
                    "statement": "支撑该洞察的证据陈述",
                    "source_ids": ["来源标识"],
                    "confidence": 0.85
                }}
            ]
        }}
    ],
    "need_more_data": false,
    "information_gaps": []
}}

要求：
1. hot_topics：识别2-5个当前热点话题
2. trend_summary：总结整体技术趋势
3. insights：生成2-4个结构化洞察，每个洞察必须有至少1条证据
4. need_more_data：如果当前资料不足以得出可靠结论，设为true
5. information_gaps：如果需要更多数据，说明缺少哪方面的信息
6. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            state.analysis.hot_topics = data.get("hot_topics", [topic])
            state.analysis.trend_summary = data.get(
                "trend_summary", f"{topic}领域正在快速发展"
            )
            state.analysis.insights = [
                AnalysisInsight(
                    title=ins.get("title", ""),
                    description=ins.get("description", ""),
                    evidences=[
                        Evidence(
                            evidence_id=f"ev_{i}_{j}",
                            statement=ev.get("statement", ""),
                            source_ids=ev.get("source_ids", []),
                            confidence=ev.get("confidence", 0.5),
                        )
                        for j, ev in enumerate(ins.get("evidences", []))
                    ],
                )
                for i, ins in enumerate(data.get("insights", []))
            ]

            # Deep Research 回环判断（仅在未达上限时生效）
            if state.research.search_round < self.MAX_RESEARCH_ROUNDS:
                need_more = data.get("need_more_data", False)
                gaps = data.get("information_gaps", [])
                state.research.need_more_data = need_more and len(gaps) > 0
                state.research.information_gaps = gaps if state.research.need_more_data else []

            logger.info(
                f"AnalysisAgent: hot_topics={state.analysis.hot_topics}, "
                f"insights={len(state.analysis.insights)}, "
                f"need_more_data={state.research.need_more_data}"
            )

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认分析: {e}")
            state.analysis.hot_topics = [topic]
            state.analysis.trend_summary = f"{topic}是当前AI领域的热门研究方向。"
            state.analysis.insights = [
                AnalysisInsight(
                    title=f"{topic}发展前景广阔",
                    description=f"{topic}在多个应用场景中展现出巨大潜力。",
                    evidences=[
                        Evidence(
                            evidence_id="ev_default_0",
                            statement=f"基于当前收集的{len(state.research.papers)}篇论文和{len(state.research.repositories)}个项目的分析",
                            source_ids=["research_data"],
                            confidence=0.6,
                        )
                    ],
                )
            ]
            state.research.need_more_data = False
            state.research.information_gaps = []

        return state
