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
"""

import logging
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from app.schemas.state.agent_state import AgentState, TaskStatus, ErrorInfo

logger = logging.getLogger(__name__)

# 最大研究轮次（与 AnalysisAgent.MAX_RESEARCH_ROUNDS 保持一致）
MAX_RESEARCH_ROUNDS = 3


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
        "planner": PlannerAgent(),
        "context": ContextAgent(),
        "research": ResearchAgent(tool_service=ToolService()),
        "analysis": AnalysisAgent(),
        "memory": MemoryAgent(),
        "report": ReportAgent(),
    }
    return _AGENTS_CACHE


# ============================================================
# 节点函数：每个节点负责调用对应 Agent 并返回更新后的 state
# ============================================================


async def planner_node(state: dict) -> dict:
    """规划节点：将用户查询转化为研究计划"""
    try:
        agent_state = AgentState.model_validate(state)
        agent = _get_agents()["planner"]
        result = await agent.run(agent_state)
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
    try:
        agent_state = AgentState.model_validate(state)
        agent = _get_agents()["context"]
        result = await agent.run(agent_state)
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
    try:
        agent_state = AgentState.model_validate(state)

        # 工作流控制：检查轮次上限，超出则强制结束回环
        if agent_state.research.search_round >= MAX_RESEARCH_ROUNDS:
            logger.info(
                f"ResearchNode: 已达最大轮次 {MAX_RESEARCH_ROUNDS}，跳过研究"
            )
            agent_state.research.need_more_data = False
            agent_state.research.information_gaps = []
            return agent_state.model_dump()

        agent = _get_agents()["research"]
        result = await agent.run(agent_state)
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
    try:
        agent_state = AgentState.model_validate(state)
        agent = _get_agents()["analysis"]
        result = await agent.run(agent_state)
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
    try:
        agent_state = AgentState.model_validate(state)
        agent = _get_agents()["memory"]
        result = await agent.run(agent_state)
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
    try:
        agent_state = AgentState.model_validate(state)
        agent = _get_agents()["report"]
        result = await agent.run(agent_state)
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
    - 如果 need_more_data=True 且 search_round < MAX_RESEARCH_ROUNDS → "research"
    - 否则 → "memory"

    M3："memory" 映射到真正的 memory_node。
    """
    agent_state = AgentState.model_validate(state)

    if agent_state.error_info is not None and agent_state.status == TaskStatus.FAILED:
        logger.warning("检测到错误状态，跳转到记忆节点进行收尾")
        return "memory"

    if (
        agent_state.research.need_more_data
        and agent_state.research.search_round < MAX_RESEARCH_ROUNDS
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
