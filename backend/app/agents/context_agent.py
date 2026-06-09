import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.schemas.state.context_state import ContextItem
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ContextAgent:
    """上下文Agent - 构建研究上下文

    职责：
    - 读取 research.topic
    - 输出 context.context_items

    M2阶段：基于当前 state 构建简单上下文
    M3阶段：接入 MemoryService 召回历史研究记忆

    约束：
    - 禁止直接访问 QdrantClient
    - 只通过 MemoryService 访问记忆（M3实现）
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """构建研究上下文"""
        state.status = TaskStatus.CONTEXT_LOADING

        topic = state.research.topic or state.user_query
        keywords = ", ".join(state.research.keywords) if state.research.keywords else topic

        # M2阶段：通过LLM生成领域背景上下文
        # M3阶段：替换为 MemoryService.recall()
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
            state.context.context_items = [
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

            logger.info(
                f"ContextAgent: 构建了 {len(state.context.context_items)} 个上下文项"
            )

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认上下文: {e}")
            state.context.context_items = [
                ContextItem(
                    item_id="ctx_0",
                    item_type="background",
                    title="领域背景",
                    content=f"{topic}是当前AI领域的研究热点之一。",
                    source_id="default",
                    relevance_score=0.5,
                )
            ]

        return state
