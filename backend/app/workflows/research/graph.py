from langgraph.graph import StateGraph, START, END
from app.schemas.state.agent_state import AgentState
from app.agents.research_agent import ResearchAgent
from app.agents.report_agent import ReportAgent

# 创建Agent实例
research_agent = ResearchAgent()
report_agent = ReportAgent()


async def research_node(state: dict) -> dict:
    """研究节点：执行资料采集"""
    agent_state = AgentState.model_validate(state)
    result = await research_agent.run(agent_state)
    return result.model_dump()


async def report_node(state: dict) -> dict:
    """报告节点：生成研究报告"""
    agent_state = AgentState.model_validate(state)
    result = await report_agent.run(agent_state)
    return result.model_dump()


def build_research_graph() -> StateGraph:
    """构建研究工作流图

    结构：START → Research → Report → END
    """
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("research", research_node)
    graph.add_node("report", report_node)

    # 添加边
    graph.add_edge(START, "research")
    graph.add_edge("research", "report")
    graph.add_edge("report", END)

    return graph
