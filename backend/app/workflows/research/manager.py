from langgraph.graph.state import CompiledStateGraph
from app.workflows.base.base_manager import BaseWorkflowManager
from app.workflows.research.graph import build_research_graph


class ResearchWorkflowManager(BaseWorkflowManager):
    """研究工作流管理器

    负责构建和执行深度研究工作流
    M1阶段：简单线性流程 (Research → Report)
    M2阶段：扩展为多Agent协作流程
    """

    def build_graph(self) -> CompiledStateGraph:
        """构建研究工作流图"""
        graph = build_research_graph()
        return graph.compile()
