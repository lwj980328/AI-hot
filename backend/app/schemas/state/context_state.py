from pydantic import BaseModel, Field


class ContextItem(BaseModel):
    """上下文项"""
    item_id: str = ""
    item_type: str = ""  # memory | trend | insight
    title: str = ""
    content: str = ""
    source_id: str = ""
    relevance_score: float = 0.0


class ContextState(BaseModel):
    """上下文状态"""
    context_items: list[ContextItem] = Field(default_factory=list)
