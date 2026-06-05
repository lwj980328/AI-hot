from abc import ABC, abstractmethod
from langgraph.graph.state import CompiledStateGraph
from app.schemas.state.agent_state import AgentState


class BaseWorkflowManager(ABC):
    """工作流管理器基类"""

    @abstractmethod
    def build_graph(self) -> CompiledStateGraph:
        """构建LangGraph图"""
        pass

    async def run(self, initial_state: AgentState) -> AgentState:
        """执行工作流"""
        graph = self.build_graph()
        # LangGraph返回字典，需要转换为AgentState
        result = await graph.ainvoke(initial_state.model_dump())
        return AgentState.model_validate(result)
