"""上下文Agent - 构建研究上下文

职责：
- 读取 research.topic
- 输出 context.context_items

实现策略（M3）：
1. 优先从 MemoryService 召回历史研究记忆
2. 有历史 → 构建 ContextItem（来源标记为 memory/trend/insight）
3. 无历史 → 回退到 LLM 生成背景知识（保证系统不中断）

约束：
- 禁止直接访问 QdrantClient
- 只通过 MemoryService 访问记忆

对应设计文档：02_Agent设计规范.md 第6节
"""

import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.schemas.state.context_state import ContextItem
from app.services.llm_service import LLMService
from app.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ContextAgent:
    """上下文Agent - 构建研究上下文"""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        memory_service: MemoryService | None = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.memory_service = memory_service or MemoryService()

    async def run(self, state: AgentState) -> AgentState:
        """构建研究上下文"""
        state.status = TaskStatus.CONTEXT_LOADING

        topic = state.research.topic or state.user_query
        keywords = ", ".join(state.research.keywords) if state.research.keywords else topic

        # ============================================================
        # 第一步：尝试从记忆系统召回历史
        # ============================================================
        context_items = await self._recall_from_memory(topic)

        # ============================================================
        # 第二步：如果记忆召回为空，回退到 LLM 生成
        # ============================================================
        if not context_items:
            logger.info(f"ContextAgent: 记忆召回为空，使用 LLM 生成上下文")
            context_items = await self._generate_from_llm(topic, keywords)

        state.context.context_items = context_items
        logger.info(
            f"ContextAgent: 构建了 {len(context_items)} 个上下文项"
        )

        return state

    async def _recall_from_memory(self, topic: str) -> list[ContextItem]:
        """从记忆系统召回历史上下文

        搜索三类记忆，按相关性转换为 ContextItem。
        不使用 topic 过滤，依赖语义搜索找到相关记忆。
        """
        try:
            # 使用用户查询进行语义搜索，不使用 topic 精确过滤
            # 因为 PlannerAgent 提炼的 topic 可能与保存时不同
            results = await self.memory_service.search_memories(
                query=topic,
                topic=None,  # 不使用 topic 过滤，依赖语义搜索
                limit=3,
            )
        except Exception as e:
            logger.warning(f"记忆召回失败: {e}")
            return []

        items = []
        item_idx = 0

        # 研究记忆 → item_type="memory"
        for r in results.get("research", []):
            payload = r.get("payload", {})
            items.append(ContextItem(
                item_id=f"mem_{item_idx}",
                item_type="memory",
                title=f"历史研究: {payload.get('report_title', topic)}",
                content=payload.get("report_summary", ""),
                source_id=payload.get("memory_id", ""),
                relevance_score=r.get("score", 0.0),
            ))
            item_idx += 1

        # 趋势快照 → item_type="trend"
        for r in results.get("trend", []):
            payload = r.get("payload", {})
            hot = ", ".join(payload.get("hot_topics", []))
            content = (
                f"{payload.get('summary', '')} "
                f"[项目数:{payload.get('project_count', 0)}, "
                f"论文数:{payload.get('paper_count', 0)}]"
            )
            items.append(ContextItem(
                item_id=f"mem_{item_idx}",
                item_type="trend",
                title=f"历史趋势: {payload.get('topic', topic)} ({hot})",
                content=content,
                source_id=payload.get("memory_id", ""),
                relevance_score=r.get("score", 0.0),
            ))
            item_idx += 1

        # 洞察记忆 → item_type="insight"
        for r in results.get("insight", []):
            payload = r.get("payload", {})
            items.append(ContextItem(
                item_id=f"mem_{item_idx}",
                item_type="insight",
                title=payload.get("insight_title", ""),
                content=payload.get("insight_description", ""),
                source_id=payload.get("memory_id", ""),
                relevance_score=r.get("score", 0.0),
            ))
            item_idx += 1

        if items:
            logger.info(f"ContextAgent: 从记忆召回 {len(items)} 个上下文项")

        return items

    async def _generate_from_llm(self, topic: str, keywords: str) -> list[ContextItem]:
        """回退方案：通过 LLM 生成领域背景上下文

        当记忆系统无结果时使用，保证系统正常运行。
        """
        prompt = f"""你是一位AI研究助手。请为以下研究主题提供背景知识摘要。

## 研究主题
{topic}

## 关键词
{keywords}

请返回JSON格式：
{{
    "context_items": [
        {{
            "item_type": "background",
            "title": "领域背景",
            "content": "对该研究领域的简要背景介绍（100字以内）"
        }},
        {{
            "item_type": "recent_progress",
            "title": "近期进展",
            "content": "该领域近期的重要进展概述（100字以内）"
        }}
    ]
}}

要求：
1. 提供2-3个上下文项
2. 内容简洁准确
3. 只返回JSON，不要其他文字"""

        try:
            data = await self.llm_service.chat_json(prompt)

            items = data.get("context_items", [])
            return [
                ContextItem(
                    item_id=f"ctx_{i}",
                    item_type=item.get("item_type", "background"),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    source_id="llm_generated",
                    relevance_score=0.8,
                )
                for i, item in enumerate(items)
            ]

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认上下文: {e}")
            return [
                ContextItem(
                    item_id="ctx_0",
                    item_type="background",
                    title="领域背景",
                    content=f"{topic}是当前AI领域的研究热点之一。",
                    source_id="default",
                    relevance_score=0.5,
                )
            ]
