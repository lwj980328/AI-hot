"""BaseTool 抽象基类

定义所有工具必须实现的统一接口和元数据。
对应 docs/03_工具设计规范.md 第4节。
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseTool(ABC):
    """工具抽象基类

    所有本地工具和 MCP 工具都必须继承此类。
    """

    name: str = ""
    description: str = ""
    version: str = "0.1.0"

    # 子类必须覆盖这两个 schema
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """统一执行入口

        Args:
            input_data: 工具输入，类型由 input_schema 定义

        Returns:
            工具输出，类型由 output_schema 定义
        """
        pass

    def get_metadata(self) -> dict:
        """获取工具元数据，供 Registry 展示"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "input_schema": self.input_schema.model_json_schema(),
            "output_schema": self.output_schema.model_json_schema(),
        }
