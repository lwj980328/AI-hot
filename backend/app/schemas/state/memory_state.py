from pydantic import BaseModel, Field


class MemoryState(BaseModel):
    """记忆状态"""
    memory_ids: list[str] = Field(default_factory=list)
    memory_updated: bool = False
