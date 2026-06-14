"""Qdrant 存储层 - 管理 Collection 和向量 CRUD

职责：
- 创建/管理 Collection（research_memory, trend_memory, insight_memory）
- 向量写入（upsert）
- 向量检索（search）
- 相似度查询（用于去重）

对应设计文档：05_记忆系统设计.md 第11节 Collection 设计
"""

import logging
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# 三个 Collection 名称（与设计文档一致）
COLLECTION_RESEARCH = "research_memory"
COLLECTION_TREND = "trend_memory"
COLLECTION_INSIGHT = "insight_memory"

ALL_COLLECTIONS = [COLLECTION_RESEARCH, COLLECTION_TREND, COLLECTION_INSIGHT]


class QdrantStore:
    """Qdrant 存储层"""

    _instance: "QdrantStore | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            settings = get_settings()
            cls._instance.client = AsyncQdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            cls._instance.dimension = settings.embedding_dimension
        return cls._instance

    async def ensure_collections(self) -> None:
        """确保所有 Collection 存在，不存在则创建

        每个 Collection 使用相同的向量维度和余弦距离。
        """
        existing = await self.client.get_collections()
        existing_names = {c.name for c in existing.collections}

        for name in ALL_COLLECTIONS:
            if name not in existing_names:
                await self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Qdrant: 创建 Collection '{name}'")
            else:
                logger.debug(f"Qdrant: Collection '{name}' 已存在")

    async def upsert(
        self,
        collection: str,
        point_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        """写入或更新一条记忆

        Args:
            collection: Collection 名称
            point_id: 记忆 ID（UUID 字符串）
            vector: 向量
            payload: 附加数据（记忆的完整字段，用于检索后还原）
        """
        await self.client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug(f"Qdrant: upsert '{point_id}' → '{collection}'")

    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 5,
        score_threshold: float = 0.0,
        topic_filter: str | None = None,
    ) -> list[dict]:
        """向量检索

        Args:
            collection: Collection 名称
            vector: 查询向量
            limit: 返回数量上限
            score_threshold: 最低相似度阈值
            topic_filter: 可选，按 topic 字段过滤

        Returns:
            结果列表，每项包含 score 和 payload
        """
        query_filter = None
        if topic_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="topic",
                        match=MatchValue(value=topic_filter),
                    )
                ]
            )

        results = await self.client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        return [
            {"id": r.id, "score": r.score, "payload": r.payload}
            for r in results.points
        ]

    async def check_duplicate(
        self,
        collection: str,
        vector: list[float],
        threshold: float = 0.95,
    ) -> bool:
        """检查是否存在高度相似的记忆（去重）

        Args:
            collection: Collection 名称
            vector: 待检查的向量
            threshold: 相似度阈值，超过则视为重复

        Returns:
            True 表示存在重复
        """
        results = await self.search(
            collection=collection,
            vector=vector,
            limit=1,
            score_threshold=threshold,
        )
        return len(results) > 0

    async def close(self) -> None:
        """关闭连接"""
        await self.client.close()
