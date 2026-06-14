"""记忆服务 - 统一记忆入口

职责：
- 保存记忆（ResearchMemory / TrendSnapshot / InsightMemory）
- 检索记忆（语义搜索）
- 查询主题历史
- 去重与污染控制

所有 Agent 通过此服务访问记忆，禁止直接操作 QdrantClient。
对应设计文档：05_记忆系统设计.md 第12-13节
"""

import uuid
import logging
from datetime import datetime
from app.memory.models import (
    MemoryRecord,
    ResearchMemory,
    TrendSnapshot,
    InsightMemory,
)
from app.memory.embedding_service import EmbeddingService
from app.memory.qdrant_store import (
    QdrantStore,
    COLLECTION_RESEARCH,
    COLLECTION_TREND,
    COLLECTION_INSIGHT,
)

logger = logging.getLogger(__name__)

# 去重阈值
DEDUP_THRESHOLD = 0.95

# 最低置信度
MIN_CONFIDENCE = 0.6


class MemoryService:
    """统一记忆服务

    单例模式：与 LLMService、EmbeddingService、QdrantStore 保持一致。
    确保所有 Agent 通过同一实例访问记忆，避免重复初始化。
    """

    _instance: "MemoryService | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.embedding = EmbeddingService()
            cls._instance.store = QdrantStore()
        return cls._instance

    async def init(self) -> None:
        """初始化：确保 Collection 存在"""
        await self.store.ensure_collections()

    # ============================================================
    # 保存
    # ============================================================

    async def save_research_memory(self, memory: ResearchMemory) -> str | None:
        """保存研究记忆

        向量化字段：report_summary
        去重：相似度 > 0.95 跳过
        """
        if not memory.report_summary:
            logger.warning("ResearchMemory 无 report_summary，跳过保存")
            return None

        vector = await self.embedding.embed(memory.report_summary)

        if await self.store.check_duplicate(COLLECTION_RESEARCH, vector, DEDUP_THRESHOLD):
            logger.info(f"ResearchMemory 重复，跳过: topic={memory.topic}")
            return None

        memory_id = memory.memory_id or str(uuid.uuid4())
        memory.memory_id = memory_id
        memory.created_at = datetime.now()

        await self.store.upsert(
            collection=COLLECTION_RESEARCH,
            point_id=memory_id,
            vector=vector,
            payload=memory.model_dump(mode="json"),
        )
        logger.info(f"保存 ResearchMemory: id={memory_id}, topic={memory.topic}")
        return memory_id

    async def save_trend_snapshot(self, snapshot: TrendSnapshot) -> str | None:
        """保存趋势快照

        向量化字段：summary
        去重：相似度 > 0.95 跳过
        """
        if not snapshot.summary:
            logger.warning("TrendSnapshot 无 summary，跳过保存")
            return None

        vector = await self.embedding.embed(snapshot.summary)

        if await self.store.check_duplicate(COLLECTION_TREND, vector, DEDUP_THRESHOLD):
            logger.info(f"TrendSnapshot 重复，跳过: topic={snapshot.topic}")
            return None

        snapshot_id = snapshot.memory_id or str(uuid.uuid4())
        snapshot.memory_id = snapshot_id
        snapshot.created_at = datetime.now()

        await self.store.upsert(
            collection=COLLECTION_TREND,
            point_id=snapshot_id,
            vector=vector,
            payload=snapshot.model_dump(mode="json"),
        )
        logger.info(f"保存 TrendSnapshot: id={snapshot_id}, topic={snapshot.topic}")
        return snapshot_id

    async def save_insight_memory(self, insight: InsightMemory) -> str | None:
        """保存洞察记忆

        向量化字段：insight_description
        污染控制：跳过 confidence < 0.6 或无 source_ids 的洞察
        去重：相似度 > 0.95 跳过
        """
        # 污染控制：检查证据
        if not insight.source_ids:
            logger.info(f"InsightMemory 无 source_ids，跳过: {insight.insight_title}")
            return None

        has_valid_evidence = any(
            ev.confidence >= MIN_CONFIDENCE for ev in insight.evidences
        )
        if not has_valid_evidence:
            logger.info(f"InsightMemory 无高置信度证据，跳过: {insight.insight_title}")
            return None

        if not insight.insight_description:
            logger.warning("InsightMemory 无 insight_description，跳过保存")
            return None

        vector = await self.embedding.embed(insight.insight_description)

        if await self.store.check_duplicate(COLLECTION_INSIGHT, vector, DEDUP_THRESHOLD):
            logger.info(f"InsightMemory 重复，跳过: {insight.insight_title}")
            return None

        insight_id = insight.memory_id or str(uuid.uuid4())
        insight.memory_id = insight_id
        insight.created_at = datetime.now()

        await self.store.upsert(
            collection=COLLECTION_INSIGHT,
            point_id=insight_id,
            vector=vector,
            payload=insight.model_dump(mode="json"),
        )
        logger.info(f"保存 InsightMemory: id={insight_id}, title={insight.insight_title}")
        return insight_id

    # ============================================================
    # 检索
    # ============================================================

    async def search_memories(
        self,
        query: str,
        topic: str | None = None,
        limit: int = 5,
    ) -> dict[str, list[dict]]:
        """语义搜索记忆

        跨三个 Collection 搜索，返回分类结果。

        Args:
            query: 搜索文本
            topic: 可选，按主题过滤
            limit: 每个 Collection 返回数量上限

        Returns:
            {"research": [...], "trend": [...], "insight": [...]}
        """
        vector = await self.embedding.embed(query)

        research_results = await self.store.search(
            collection=COLLECTION_RESEARCH,
            vector=vector,
            limit=limit,
            topic_filter=topic,
        )
        trend_results = await self.store.search(
            collection=COLLECTION_TREND,
            vector=vector,
            limit=limit,
            topic_filter=topic,
        )
        insight_results = await self.store.search(
            collection=COLLECTION_INSIGHT,
            vector=vector,
            limit=limit,
            topic_filter=topic,
        )

        logger.info(
            f"记忆检索: query='{query}', "
            f"research={len(research_results)}, "
            f"trend={len(trend_results)}, "
            f"insight={len(insight_results)}"
        )

        return {
            "research": research_results,
            "trend": trend_results,
            "insight": insight_results,
        }

    async def get_topic_history(self, topic: str) -> list[TrendSnapshot]:
        """获取某主题的历史趋势数据

        Args:
            topic: 主题名称

        Returns:
            该主题的历史趋势快照列表，按时间排序
        """
        results = await self.store.search(
            collection=COLLECTION_TREND,
            vector=await self.embedding.embed(topic),
            limit=20,
            topic_filter=topic,
        )
        snapshots = []
        for r in results:
            try:
                snapshots.append(TrendSnapshot(**r["payload"]))
            except Exception as e:
                logger.warning(f"解析 TrendSnapshot 失败: {e}")

        snapshots.sort(key=lambda s: s.created_at)
        return snapshots
