"""研究工作流图定义

结构（M3）：
    START → Planner → Context → Research → Analysis
                                          ↓
                                    continue_research (条件边)
                                     ↙        ↘
                                Research      Memory → Report → END
                                (回环)

Deep Research 回环：
    Analysis 发现信息不足时，回到 Research 补充数据，
    最多循环 MAX_RESEARCH_ROUNDS 轮。

M3 变更：
    - 新增 memory_node（调用 MemoryAgent 写入长期记忆）
    - 条件边 "memory" 从直接映射 report 改为映射 memory_node

M8 重构：
    - 使用 WorkflowContext 替代全局变量，遵循 04_Workflow设计规范.md
    - 移除 AgentState.current_node，前端根据任务状态推断
    - 工具调用记录存储在独立的 tool_execution_logs 表中
    - 节点执行日志存储在独立的 node_execution_logs 表中
"""

import json
import logging
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from app.schemas.state.agent_state import AgentState, TaskStatus, ErrorInfo
from app.workflows.base.workflow_context import WorkflowContext
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# 工作流上下文（通过 build_research_graph 的参数注入）
_workflow_context: WorkflowContext | None = None


def set_workflow_context(context: WorkflowContext) -> None:
    """设置工作流上下文"""
    global _workflow_context
    _workflow_context = context


# ============================================================
# 延迟导入 Agent（避免循环依赖）
# ============================================================

_AGENTS_CACHE: dict[str, object] | None = None


def _get_agents():
    """延迟导入所有 Agent，避免 app.agents ↔ app.workflows 循环导入

    使用模块级缓存，只在首次调用时创建实例，后续复用。
    """
    global _AGENTS_CACHE
    if _AGENTS_CACHE is not None:
        return _AGENTS_CACHE

    from app.agents.planner_agent import PlannerAgent
    from app.agents.context_agent import ContextAgent
    from app.agents.research_agent import ResearchAgent
    from app.agents.analysis_agent import AnalysisAgent
    from app.agents.memory_agent import MemoryAgent
    from app.agents.report_agent import ReportAgent
    from app.tools.base.tool_service import ToolService

    _AGENTS_CACHE = {
        "planner": PlannerAgent(tool_service=ToolService()),
        "context": ContextAgent(),
        "research": ResearchAgent(tool_service=ToolService()),
        "analysis": AnalysisAgent(),
        "memory": MemoryAgent(),
        "report": ReportAgent(),
    }
    return _AGENTS_CACHE


# ============================================================
# 辅助函数：构建节点输出摘要
# ============================================================


def _build_planner_summary(state: AgentState) -> str:
    """构建 Planner 节点输出摘要"""
    data = {
        "topic": state.research.topic,
        "keywords": state.research.keywords,
        "data_sources": state.research.data_sources,
    }
    return json.dumps(data, ensure_ascii=False)


def _build_context_summary(state: AgentState) -> str:
    """构建 Context 节点输出摘要"""
    items = [
        {"type": c.item_type, "title": c.title, "content": c.content[:100]}
        for c in state.context.context_items
    ]
    return json.dumps(items, ensure_ascii=False)


def _build_research_summary(state: AgentState) -> str:
    """构建 Research 节点输出摘要"""
    data = {
        "papers": [{"title": p.title, "summary": p.summary[:100]} for p in state.research.papers[:3]],
        "repositories": [{"title": r.title, "stars": r.stars} for r in state.research.repositories[:3]],
        "models": [{"title": m.title, "downloads": m.downloads} for m in state.research.models[:3]],
        "search_round": state.research.search_round,
    }
    return json.dumps(data, ensure_ascii=False)


def _build_analysis_summary(state: AgentState) -> str:
    """构建 Analysis 节点输出摘要"""
    data = {
        "hot_topics": state.analysis.hot_topics,
        "trend_summary": state.analysis.trend_summary[:200] if state.analysis.trend_summary else "",
        "insights": [{"title": i.title, "description": i.description[:100]} for i in state.analysis.insights],
        "need_more_data": state.research.need_more_data,
        "information_gaps": state.research.information_gaps,
    }
    return json.dumps(data, ensure_ascii=False)


def _build_memory_summary(state: AgentState) -> str:
    """构建 Memory 节点输出摘要"""
    data = {
        "memory_ids": state.memory.memory_ids,
        "memory_updated": state.memory.memory_updated,
    }
    return json.dumps(data, ensure_ascii=False)


def _build_report_summary(state: AgentState) -> str:
    """构建 Report 节点输出摘要"""
    data = {
        "title": state.report.title,
        "summary": state.report.summary,
        "content_length": len(state.report.markdown_content),
        "is_fallback": state.report.is_fallback,
    }
    return json.dumps(data, ensure_ascii=False)


# ============================================================
# 节点函数：每个节点负责调用对应 Agent 并返回更新后的 state
# ============================================================


async def planner_node(state: dict) -> dict:
    """规划节点：将用户查询转化为研究计划"""
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.PLANNING.value)
        agent = _get_agents()["planner"]
        result = await agent.run(agent_state)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="planner",
                input_summary=json.dumps({"user_query": agent_state.user_query}, ensure_ascii=False),
                output_summary=_build_planner_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"PlannerNode 异常: {e}")
        agent_state = AgentState.model_validate(state)
        agent_state.status = TaskStatus.FAILED
        agent_state.error_info = ErrorInfo(
            error_type=type(e).__name__,
            error_message=str(e),
            node_name="planner",
            created_at=datetime.now(),
        )
        return agent_state.model_dump()


async def context_node(state: dict) -> dict:
    """上下文节点：构建研究所需上下文

    M3：优先从记忆系统召回历史研究记忆。
    """
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.CONTEXT_LOADING.value)
        agent = _get_agents()["context"]
        result = await agent.run(agent_state)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="context",
                input_summary=json.dumps({"topic": agent_state.research.topic}, ensure_ascii=False),
                output_summary=_build_context_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"ContextNode 异常: {e}")
        agent_state = AgentState.model_validate(state)
        agent_state.status = TaskStatus.FAILED
        agent_state.error_info = ErrorInfo(
            error_type=type(e).__name__,
            error_message=str(e),
            node_name="context",
            created_at=datetime.now(),
        )
        return agent_state.model_dump()


async def research_node(state: dict) -> dict:
    """研究节点：执行资料采集

    职责：调度 ResearchAgent，不做业务逻辑。
    轮次上限检查是工作流控制逻辑，保留在节点层。
    search_round 递增由 ResearchAgent 负责。
    """
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.RESEARCHING.value)

        # 工作流控制：检查轮次上限，超出则强制结束回环
        settings = get_settings()
        if agent_state.research.search_round >= settings.max_research_rounds:
            logger.info(
                f"ResearchNode: 已达最大轮次 {settings.max_research_rounds}，跳过研究"
            )
            agent_state.research.need_more_data = False
            agent_state.research.information_gaps = []
            return agent_state.model_dump()

        agent = _get_agents()["research"]
        result = await agent.run(agent_state)

        # 保存工具调用记录到独立表
        if _workflow_context and hasattr(result, '_tool_calls_data'):
            await _workflow_context.save_tool_calls(result._tool_calls_data)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="research",
                input_summary=json.dumps({"topic": agent_state.research.topic, "keywords": agent_state.research.keywords}, ensure_ascii=False),
                output_summary=_build_research_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"ResearchNode 异常: {e}")
        agent_state = AgentState.model_validate(state)
        agent_state.status = TaskStatus.FAILED
        agent_state.error_info = ErrorInfo(
            error_type=type(e).__name__,
            error_message=str(e),
            node_name="research",
            created_at=datetime.now(),
        )
        return agent_state.model_dump()


async def analysis_node(state: dict) -> dict:
    """分析节点：从原始资料中提取结构化知识"""
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.ANALYZING.value)
        agent = _get_agents()["analysis"]
        result = await agent.run(agent_state)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="analysis",
                input_summary=json.dumps({"papers_count": len(agent_state.research.papers), "repos_count": len(agent_state.research.repositories)}, ensure_ascii=False),
                output_summary=_build_analysis_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"AnalysisNode 异常: {e}")
        agent_state = AgentState.model_validate(state)
        agent_state.status = TaskStatus.FAILED
        agent_state.error_info = ErrorInfo(
            error_type=type(e).__name__,
            error_message=str(e),
            node_name="analysis",
            created_at=datetime.now(),
        )
        return agent_state.model_dump()


async def memory_node(state: dict) -> dict:
    """记忆节点：将研究结果写入长期记忆

    M3 新增节点。
    读取 state.research + state.analysis + state.report，
    构建 ResearchMemory / TrendSnapshot / InsightMemory 并保存到 Qdrant。
    """
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.MEMORY_UPDATING.value)
        agent = _get_agents()["memory"]
        result = await agent.run(agent_state)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="memory",
                input_summary=json.dumps({"topic": agent_state.research.topic}, ensure_ascii=False),
                output_summary=_build_memory_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"MemoryNode 异常: {e}")
        # 记忆写入失败不应阻断流程，降级处理
        agent_state = AgentState.model_validate(state)
        agent_state.memory.memory_updated = False
        logger.warning("MemoryNode 失败，降级继续执行")
        return agent_state.model_dump()


async def report_node(state: dict) -> dict:
    """报告节点：生成最终研究报告"""
    start_time = datetime.now()
    try:
        agent_state = AgentState.model_validate(state)
        if _workflow_context:
            await _workflow_context.update_status(TaskStatus.REPORTING.value)
        agent = _get_agents()["report"]
        result = await agent.run(agent_state)

        # 保存节点执行日志
        if _workflow_context:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            await _workflow_context.save_node_log(
                node_name="report",
                input_summary=json.dumps({"topic": agent_state.research.topic}, ensure_ascii=False),
                output_summary=_build_report_summary(result),
                duration_ms=duration_ms,
            )

        return result.model_dump()
    except Exception as e:
        logger.error(f"ReportNode 异常: {e}")
        agent_state = AgentState.model_validate(state)
        agent_state.status = TaskStatus.FAILED
        agent_state.error_info = ErrorInfo(
            error_type=type(e).__name__,
            error_message=str(e),
            node_name="report",
            created_at=datetime.now(),
        )
        return agent_state.model_dump()


# ============================================================
# 条件边：决定 Analysis 之后的流转方向
# ============================================================


def continue_research(state: dict) -> str:
    """条件边：决定是否继续研究

    逻辑（符合 04_Workflow设计规范.md 第 5 节）：
    - 如果 need_more_data=True 且 search_round < max_research_rounds → "research"
    - 否则 → "memory"

    M3："memory" 映射到真正的 memory_node。
    """
    agent_state = AgentState.model_validate(state)

    if agent_state.error_info is not None and agent_state.status == TaskStatus.FAILED:
        logger.warning("检测到错误状态，跳转到记忆节点进行收尾")
        return "memory"

    settings = get_settings()
    if (
        agent_state.research.need_more_data
        and agent_state.research.search_round < settings.max_research_rounds
    ):
        logger.info(
            f"Deep Research: need_more_data=True, "
            f"round={agent_state.research.search_round}, "
            f"gaps={agent_state.research.information_gaps}"
        )
        return "research"

    logger.info("研究数据充足，进入记忆写入阶段")
    return "memory"


# ============================================================
# 图构建
# ============================================================


def build_research_graph() -> StateGraph:
    """构建研究工作流图

    结构（M3）：
        START → Planner → Context → Research → Analysis
                                              ↓
                                        continue_research (条件边)
                                         ↙        ↘
                                    Research      Memory → Report → END
                                    (回环)
    """
    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("planner", planner_node)
    graph.add_node("context", context_node)
    graph.add_node("research", research_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("memory", memory_node)
    graph.add_node("report", report_node)

    # 注册边
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "context")
    graph.add_edge("context", "research")
    graph.add_edge("research", "analysis")

    # 条件边：analysis → research（回环）或 memory（记忆写入）
    graph.add_conditional_edges(
        "analysis",
        continue_research,
        {
            "research": "research",
            "memory": "memory",
        },
    )

    # 记忆写入 → 报告生成 → 结束
    graph.add_edge("memory", "report")
    graph.add_edge("report", END)

    return graph
