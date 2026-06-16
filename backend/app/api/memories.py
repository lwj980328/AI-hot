"""记忆 API 路由

提供记忆检索、搜索、统计接口。
遵循 docs/08_API设计.md 规范，使用 /api/v1 前缀。
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.schemas.api.common import ApiResponse
from app.schemas.api.memory_response import (
    MemoryItemResponse,
    MemorySearchResponse,
    MemoryStatsResponse,
)
from app.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter()


def _to_memory_item(data: dict, score: float = 0.0) -> MemoryItemResponse:
    """将 Qdrant 返回的数据转换为 MemoryItemResponse

    Qdrant 返回格式: {"id": ..., "score": ..., "payload": {...}}
    需要先提取 payload，再构建响应。
    """
    # 提取 payload（如果存在）
    payload = data.get("payload", data)

    # 处理 created_at 字段：空字符串或无效值设为 None
    created_at = payload.get("created_at")
    if not created_at or created_at == "":
        created_at = None

    return MemoryItemResponse(
        memory_id=payload.get("memory_id", data.get("id", "")),
        memory_type=payload.get("memory_type", ""),
        topic=payload.get("topic", ""),
        summary=payload.get("summary", ""),
        created_at=created_at,
        source_ids=payload.get("source_ids", []),
        score=score if score > 0 else data.get("score", 0.0),
        # Research Memory
        report_title=payload.get("report_title"),
        report_summary=payload.get("report_summary"),
        # Trend Snapshot
        hot_topics=payload.get("hot_topics"),
        project_count=payload.get("project_count"),
        paper_count=payload.get("paper_count"),
        model_count=payload.get("model_count"),
        confidence_score=payload.get("confidence_score"),
        # Insight Memory
        insight_title=payload.get("insight_title"),
        insight_description=payload.get("insight_description"),
        evidences=payload.get("evidences"),
    )


@router.get("/search", response_model=ApiResponse[MemorySearchResponse])
async def search_memories(
    q: str = Query(..., description="搜索关键词"),
    topic: str | None = Query(None, description="按主题过滤"),
    limit: int = Query(5, ge=1, le=20, description="每类记忆返回数量"),
):
    """语义搜索记忆

    跨三个 Collection 搜索（research、trend、insight），返回分类结果。
    """
    try:
        memory_service = MemoryService()
        results = await memory_service.search_memories(
            query=q, topic=topic, limit=limit
        )

        # 转换为响应模型
        research_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("research", [])
        ]
        trend_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("trend", [])
        ]
        insight_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("insight", [])
        ]

        total = len(research_items) + len(trend_items) + len(insight_items)

        response = MemorySearchResponse(
            research=research_items,
            trend=trend_items,
            insight=insight_items,
            total=total,
        )
        return ApiResponse.ok(response)
    except Exception as e:
        logger.error(f"记忆搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"记忆搜索失败: {str(e)}")


@router.get("", response_model=ApiResponse[MemorySearchResponse])
async def list_memories(
    memory_type: str | None = Query(
        None, description="记忆类型: research | trend | insight"
    ),
    topic: str | None = Query(None, description="按主题过滤"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
):
    """获取记忆列表

    按类型分页查询，不传 type 则返回所有类型。
    """
    try:
        memory_service = MemoryService()

        # 使用空查询获取所有记忆
        results = await memory_service.search_memories(
            query=topic or "AI research",  # 使用主题或默认查询
            topic=topic,
            limit=limit,
        )

        # 按类型过滤
        research_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("research", [])
        ]
        trend_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("trend", [])
        ]
        insight_items = [
            _to_memory_item(r, r.get("score", 0.0))
            for r in results.get("insight", [])
        ]

        # 如果指定了类型，只返回该类型
        if memory_type == "research":
            trend_items = []
            insight_items = []
        elif memory_type == "trend":
            research_items = []
            insight_items = []
        elif memory_type == "insight":
            research_items = []
            trend_items = []

        total = len(research_items) + len(trend_items) + len(insight_items)

        response = MemorySearchResponse(
            research=research_items,
            trend=trend_items,
            insight=insight_items,
            total=total,
        )
        return ApiResponse.ok(response)
    except Exception as e:
        logger.error(f"获取记忆列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆列表失败: {str(e)}")


@router.get("/stats", response_model=ApiResponse[MemoryStatsResponse])
async def get_memory_stats():
    """获取记忆统计信息

    返回各类记忆的数量统计。
    """
    try:
        memory_service = MemoryService()

        # 搜索空查询获取各 Collection 的数据量
        # 注意：Qdrant 没有直接的 count API，需要通过搜索获取
        results = await memory_service.search_memories(
            query="AI research", limit=100
        )

        research_count = len(results.get("research", []))
        trend_count = len(results.get("trend", []))
        insight_count = len(results.get("insight", []))

        response = MemoryStatsResponse(
            research_count=research_count,
            trend_count=trend_count,
            insight_count=insight_count,
            total=research_count + trend_count + insight_count,
        )
        return ApiResponse.ok(response)
    except Exception as e:
        logger.error(f"获取记忆统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆统计失败: {str(e)}")
