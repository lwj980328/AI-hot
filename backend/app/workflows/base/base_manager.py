from abc import ABC, abstractmethod
from langgraph.graph.state import CompiledStateGraph
from app.schemas.state.agent_state import AgentState


class BaseWorkflowManager(ABC):
    """工作流管理器基类

    接口规范（10_WorkflowManager设计.md 第 15 节）：
    - async def run(task_id: str, user_query: str) -> AgentState
    - def build_graph(self) -> CompiledStateGraph
    """

    @abstractmethod
    def build_graph(self) -> CompiledStateGraph:
        """构建LangGraph图"""
        pass

    async def run(self, task_id: str, user_query: str) -> AgentState:
        """执行工作流

        Args:
            task_id: 任务ID
            user_query: 用户查询

        Returns:
            AgentState: 最终状态
        """
        initial_state = AgentState(
            task_id=task_id,
            user_query=user_query,
        )
        graph = self.build_graph()
        result = await graph.ainvoke(initial_state.model_dump())
        return AgentState.model_validate(result)
