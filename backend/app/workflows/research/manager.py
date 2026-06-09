from langgraph.graph.state import CompiledStateGraph
from app.workflows.base.base_manager import BaseWorkflowManager
from app.workflows.research.graph import build_research_graph


class ResearchWorkflowManager(BaseWorkflowManager):
    """研究工作流管理器

    负责构建和执行深度研究工作流
    M2阶段：多Agent协作流程 (Planner → Context → Research → Analysis → Report)
    支持 Deep Research 回环（Analysis 发现信息不足时回到 Research 补充数据）
    """

    def build_graph(self) -> CompiledStateGraph:
        """构建研究工作流图"""
        graph = build_research_graph()
        return graph.compile()
