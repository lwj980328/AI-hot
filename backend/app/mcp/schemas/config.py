"""MCP Server 配置模型

对应 docs/06_MCP设计规范.md 第6节。
"""

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """MCP Server 统一配置"""

    server_id: str = Field(..., description="MCP Server 唯一标识")
    name: str = Field(..., description="显示名称")
    transport: str = Field(..., description="传输协议: stdio | sse | http")
    command: str | None = Field(None, description="STDIO: 可执行命令")
    args: list[str] | None = Field(None, description="STDIO: 命令参数")
    url: str | None = Field(None, description="SSE/HTTP: 服务地址")
    env: dict[str, str] = Field(default_factory=dict, description="环境变量")
    enabled: bool = Field(True, description="是否启用")
    timeout: int = Field(30, description="超时时间(秒)")
    max_retry: int = Field(3, description="最大重试次数")
