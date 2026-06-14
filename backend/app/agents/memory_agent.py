"""记忆Agent - 负责更新长期记忆

职责：
- 读取 state.research, state.analysis, state.report
- 构建 ResearchMemory / TrendSnapshot / InsightMemory
- 调用 MemoryService 写入 Qdrant
- 写入结果到 state.memory

约束：
- 只负责写入（Update），不负责召回（Recall）
- 召回职责属于 ContextAgent
- 禁止直接访问 QdrantClient

对应设计文档：02_Agent设计规范.md 第9节
"""

import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.memory.memory_service import MemoryService
from app.memory.models import ResearchMemory, TrendSnapshot, InsightMemory, MemoryEvidence

logger = logging.getLogger(__name__)


class MemoryAgent:
    """记忆Agent - 写入长期记忆"""

    def __init__(self, memory_service: MemoryService | None = None):
        self.memory_service = memory_service or MemoryService()

    async def run(self, state: AgentState) -> AgentState:
        """写入长期记忆

        从 state 中提取研究结果、分析洞察，构建三类记忆并保存。
        """
        state.status = TaskStatus.MEMORY_UPDATING
        memory_ids = []

        topic = state.research.topic or state.user_query

        # 1. 保存 ResearchMemory（完整研究报告）
        if state.report.markdown_content:
            # report_summary 可能为空，用 title 或 markdown 前200字作为回退
            report_summary = state.report.summary
            if not report_summary:
                report_summary = state.report.title or state.report.markdown_content[:200]

            research_mem = ResearchMemory(
                topic=topic,
                summary=report_summary,
                source_ids=[p.url for p in state.research.papers],
                report_title=state.report.title,
                report_summary=report_summary,
                report_markdown=state.report.markdown_content,
            )
            mid = await self.memory_service.save_research_memory(research_mem)
            if mid:
                memory_ids.append(mid)

        # 2. 保存 TrendSnapshot（趋势快照）
        trend_summary = state.analysis.trend_summary
        if not trend_summary and state.analysis.hot_topics:
            trend_summary = f"热点: {', '.join(state.analysis.hot_topics)}"
        if trend_summary:
            trend_snap = TrendSnapshot(
                topic=topic,
                summary=trend_summary,
                source_ids=[p.url for p in state.research.papers],
                hot_topics=state.analysis.hot_topics,
                project_count=len(state.research.repositories),
                paper_count=len(state.research.papers),
                model_count=len(state.research.models),
                confidence_score=self._calc_confidence(state),
            )
            mid = await self.memory_service.save_trend_snapshot(trend_snap)
            if mid:
                memory_ids.append(mid)

        # 3. 保存 InsightMemory（结构化洞察）
        for insight in state.analysis.insights:
            # 收集所有来源 ID
            source_ids = []
            for ev in insight.evidences:
                source_ids.extend(ev.source_ids)

            insight_mem = InsightMemory(
                topic=topic,
                summary=insight.description,
                source_ids=list(set(source_ids)),
                insight_title=insight.title,
                insight_description=insight.description,
                evidences=[
                    MemoryEvidence(
                        statement=ev.statement,
                        source_ids=ev.source_ids,
                        confidence=ev.confidence,
                    )
                    for ev in insight.evidences
                ],
            )
            mid = await self.memory_service.save_insight_memory(insight_mem)
            if mid:
                memory_ids.append(mid)

        state.memory.memory_ids = memory_ids
        state.memory.memory_updated = len(memory_ids) > 0

        logger.info(
            f"MemoryAgent: 写入 {len(memory_ids)} 条记忆, "
            f"topic={topic}"
        )

        return state

    def _calc_confidence(self, state: AgentState) -> float:
        """计算趋势快照的置信度

        基于证据平均置信度和数据量综合评估。
        """
        if not state.analysis.insights:
            return 0.5

        confidences = [
            ev.confidence
            for ins in state.analysis.insights
            for ev in ins.evidences
        ]
        if not confidences:
            return 0.5

        avg_confidence = sum(confidences) / len(confidences)
        # 数据量加成：论文+项目越多，置信度越高
        data_bonus = min(0.1, (len(state.research.papers) + len(state.research.repositories)) * 0.01)
        return min(1.0, avg_confidence + data_bonus)
