# MCP设计规范

---

# 1. 文档目标

本文档定义系统MCP（Model Context Protocol）接入架构。

本项目中：

MCP不是某一个工具。

而是一套：

```text
能力接入标准
(Capability Integration Standard)
```

用于统一接入：

- Github
- Search
- Browser
- Notion
- Slack
- Filesystem
- 自定义工具

等外部能力。

---

# 2. 设计目标

实现：

```text
Agent
↓
ToolRegistry
↓
MCP Tool
↓
MCP Client
↓
MCP Server
```

架构。

Agent无需感知：

- API
- SDK
- HTTP
- MCP

之间的差异。

---

# 3. 设计原则

---

## 原则一

Agent不直接访问MCP

禁止：

```python
ResearchAgent(
    github_mcp_client
)
```

---

必须通过：

```python
ToolRegistry
```

访问。

---

## 原则二

MCP统一映射为Tool

Agent眼中：

```python
GithubTool
```

与：

```python
ArxivTool
```

没有区别。

---

## 原则三

支持动态发现

系统启动时自动发现：

```text
所有可用MCP能力
```

---

## 原则四

支持故障隔离

单个MCP故障：

不能导致Workflow失败。

---

## 原则五

支持多协议

支持：

```text
STDIO

SSE

HTTP Stream
```

---

# 4. 系统架构

```text
Agent
  │
  ▼
ToolRegistry
  │
  ▼
BaseTool
  │
 ┌─────────────┐
 │             │
 ▼             ▼
LocalTool    MCPTool
                │
                ▼
           MCPAdapter
                │
                ▼
         MCPClientManager
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
   STDIO      SSE       HTTP
      │         │         │
      ▼         ▼         ▼
   MCP Server MCP Server MCP Server
```

---

# 5. MCP支持范围

当前支持：

```text
本地MCP

远程MCP

企业内部MCP
```

---

未来支持：

```text
多租户MCP

认证MCP

权限MCP
```

---

# 6. MCPServerConfig

所有MCP统一配置。

---

```python
class MCPServerConfig(BaseModel):

    server_id: str

    name: str

    transport: str

    enabled: bool = True

    timeout: int = 30

    metadata: dict = {}
```

---

# 7. Transport类型

---

## STDIO

本地进程模式。

---

示例：

```python
transport="stdio"
```

---

配置：

```json
{
    "command": "python",
    "args": ["github_server.py"]
}
```

---

## SSE

Server-Sent Events模式。

---

示例：

```python
transport="sse"
```

---

配置：

```json
{
    "url": "http://localhost:8000/sse"
}
```

---

## HTTP

HTTP Stream模式。

---

示例：

```python
transport="http"
```

---

配置：

```json
{
    "url": "https://api.xxx.com/mcp"
}
```

---

# 8. MCP能力模型

---

## MCPToolMetadata

```python
class MCPToolMetadata(BaseModel):

    tool_name: str

    description: str

    input_schema: dict

    output_schema: dict
```

---

作用：

描述MCP暴露的能力。

---

示例：

```python
tool_name="search_repositories"
```

---

# 9. MCPClient抽象

---

## BaseMCPClient

```python
class BaseMCPClient(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def list_tools(self):
        pass

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: dict
    ):
        pass
```

---

# 10. STDIO客户端

---

```python
class STDIOMCPClient(
    BaseMCPClient
):
    pass
```

---

职责：

```text
启动本地进程

管理STDIO通信

进程生命周期管理
```

---

# 11. SSE客户端

---

```python
class SSEMCPClient(
    BaseMCPClient
):
    pass
```

---

职责：

```text
连接SSE服务

接收事件流

发送工具调用
```

---

# 12. HTTP客户端

---

```python
class HTTPMCPClient(
    BaseMCPClient
):
    pass
```

---

职责：

```text
远程MCP调用

HTTP流管理
```

---

# 13. MCPClientFactory

统一创建客户端。

---

```python
class MCPClientFactory:

    def create(
        self,
        config: MCPServerConfig
    ) -> BaseMCPClient:
        pass
```

---

规则：

```text
stdio
→ STDIOMCPClient

sse
→ SSEMCPClient

http
→ HTTPMCPClient
```

---

# 14. MCPClientManager

负责：

```text
连接

断开

重连

健康检查
```

---

定义：

```python
class MCPClientManager:
    pass
```

---

维护：

```python
clients: dict[
    str,
    BaseMCPClient
]
```

---

# 15. MCPDiscoveryService

系统启动时执行。

---

职责：

```text
发现MCP能力
```

---

流程：

```text
读取配置
↓
连接MCP
↓
list_tools()
↓
获得能力列表
↓
注册ToolRegistry
```

---

# 16. MCPAdapter

核心适配层。

---

职责：

```text
MCP Tool
↓
BaseTool
```

转换。

---

定义：

```python
class MCPAdapter:
    pass
```

---

# 17. MCPTool

统一MCP工具实现。

---

继承：

```python
BaseTool
```

---

定义：

```python
class MCPTool(
    BaseTool
):
    pass
```

---

职责：

```text
接收Tool调用

转发至MCP

返回结果
```

---

# 18. MCPTool执行流程

```text
Agent
↓
ToolRegistry
↓
MCPTool
↓
MCPClient
↓
MCP Server
↓
返回结果
```

---

Agent无需知道：

```text
Github

Notion

Slack

Filesystem
```

区别。

---

# 19. ToolRegistry集成

启动时：

```python
DiscoveryService
```

自动发现：

```text
search_repositories

search_papers

read_file
```

等能力。

---

转换：

```python
MCPTool
```

---

注册：

```python
ToolRegistry
```

---

# 20. 权限控制

新增：

```python
ToolPermission
```

---

定义：

```python
class ToolPermission(
    Enum
):
```

---

权限：

```text
READ

WRITE

DELETE

EXECUTE
```

---

Tool注册时声明。

---

Agent只能调用：

```text
允许权限范围内
```

工具。

---

# 21. 故障隔离

---

## MCP不可用

返回：

```python
ToolExecutionError
```

---

禁止：

```text
Workflow崩溃
```

---

## 超时

统一超时：

```python
timeout=30
```

---

超时后：

```python
ToolExecutionError
```

---

## 自动重连

支持：

```python
max_retry=3
```

---

# 22. 监控指标

记录：

```text
调用次数

成功率

失败率

平均响应时间
```

---

定义：

```python
ToolMetrics
```

---

供未来：

```text
Prometheus

Grafana
```

接入。

---

# 23. MCP配置目录

```text
backend/config/mcp/

├── github.yaml

├── search.yaml

├── browser.yaml

├── filesystem.yaml
```

---

# 24. MCP模块目录

```text
backend/app/mcp/

├── clients/

│   ├── base_client.py

│   ├── stdio_client.py

│   ├── sse_client.py

│   └── http_client.py

├── adapters/

│   └── mcp_adapter.py

├── discovery/

│   └── discovery_service.py

├── manager/

│   └── client_manager.py

├── schemas/

│   ├── config.py

│   ├── metadata.py

│   └── permissions.py

└── tools/

    └── mcp_tool.py
```

---

# 25. MVP阶段实现范围

第一阶段仅实现：

```text
STDIO Client

Github MCP

Filesystem MCP
```

---

第二阶段实现：

```text
SSE Client

Search MCP
```

---

第三阶段实现：

```text
HTTP Client

Browser MCP

Notion MCP
```

---

# 26. 与Tool系统关系

依赖：

```text
03_工具设计规范.md
```

---

MCPTool必须继承：

```python
BaseTool
```

---

ToolRegistry是唯一入口。

---

禁止：

```python
Agent
↓
MCPClient
```

直接调用。

---

# 27. 与Workflow关系

Workflow不感知MCP。

---

Workflow只调用：

```text
ResearchAgent
```

---

ResearchAgent只调用：

```text
ToolRegistry
```

---

MCP属于基础设施层。

---

# 28. 文档依赖

依赖：

- 02_Agent设计规范.md
- 03\_工具设计规范.md

后续：

- 07\_数据库设计.md
- 08_API设计.md

必须遵循本文件定义的MCP架构。
