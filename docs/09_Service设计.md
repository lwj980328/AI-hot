# Service设计

# 1. 文档目标

定义系统 Service 层设计规范。

Service 层是系统业务逻辑中心。

负责：

```text
业务编排

状态管理

工作流协调

数据持久化协调

记忆管理协调
```

不负责：

```text
HTTP

数据库

Qdrant

MCP通信
```

---

# 2. 设计原则

---

## 原则一

Service 是唯一业务入口。

---

允许：

```text
API
↓
Service
```

---

允许：

```text
Workflow
↓
Service
```

---

禁止：

```text
API
↓
Repository
```

---

禁止：

```text
Workflow
↓
Repository
```

---

## 原则二

Service 不感知数据库实现。

---

允许：

```python
task_repository
```

---

禁止：

```python
AsyncSession
```

直接出现。

---

## 原则三

一个 Service 一个领域。

---

例如：

```text
TaskService

ReportService

MemoryService
```

---

禁止：

```text
GodService
```

---

# 3. 服务架构

```text
                API

                 │

                 ▼

             Service

                 │

      ┌──────────┼──────────┐

      ▼          ▼          ▼

 Repository   Memory     Workflow

                 │

                 ▼

             Qdrant
```

---

# 4. Service目录结构

```text
backend/app/services/

├── task_service.py

├── workflow_service.py

├── report_service.py

├── source_service.py

├── memory_service.py

├── tool_service.py

├── monitoring_service.py

└── interfaces/
```

---

# 5. BaseService

所有Service统一继承。

```python
class BaseService:
    pass
```

---

职责：

```text
日志

异常转换

事务边界
```

---

# 6. TaskService

负责：

```text
研究任务生命周期
```

---

职责：

```text
创建任务

查询任务

更新状态

任务列表
```

---

接口：

```python
class TaskService:

    async def create_task()

    async def get_task()

    async def list_tasks()

    async def update_status()
```

---

依赖：

```python
TaskRepository
```

---

# 7. WorkflowService

系统核心服务。

---

负责：

```text
启动Workflow

重跑Workflow

Workflow状态同步

Workflow结果保存
```

---

接口：

```python
class WorkflowService:

    async def run_task()

    async def rerun_task()

    async def get_run()

    async def list_runs()
```

---

依赖：

```python
WorkflowRunRepository

TaskRepository

GraphWorkflow
```

---

# 8. Workflow执行流程

```text
run_task()

    ↓

创建WorkflowRun

    ↓

创建AgentState

    ↓

执行LangGraph

    ↓

保存结果

    ↓

更新状态
```

---

# 9. ReportService

负责：

```text
研究报告管理
```

---

接口：

```python
class ReportService:

    async def save_report()

    async def get_report()

    async def search_reports()
```

---

职责：

```text
PostgreSQL保存

Qdrant双写
```

---

# 10. SourceService

负责：

```text
研究资料管理
```

---

接口：

```python
class SourceService:

    async def save_sources()

    async def get_source()

    async def list_sources()
```

---

职责：

```text
Source双写

Source查询
```

---

# 11. MemoryService

本系统核心服务之一。

---

负责：

```text
长期记忆管理
```

---

依赖：

```python
Qdrant
```

---

接口：

```python
class MemoryService:

    async def save_research_memory()

    async def save_trend_snapshot()

    async def save_insight()

    async def search()

    async def get_topic_history()
```

---

说明：

```text
ContextAgent

MemoryAgent

均通过MemoryService访问记忆
```

---

# 12. ToolService

工具统一入口。

---

职责：

```text
ToolRegistry封装

工具调用

权限检查

日志记录
```

---

接口：

```python
class ToolService:

    async def execute_tool()

    async def list_tools()
```

---

执行流程：

```text
ToolService

↓

ToolRegistry

↓

BaseTool

↓

Local Tool
或
MCP Tool
```

---

# 13. MonitoringService

负责：

```text
系统监控
```

---

统计：

```text
任务数

工作流数

工具调用数

成功率

失败率
```

---

接口：

```python
class MonitoringService:

    async def get_metrics()
```

---

# 14. Workflow与Service关系

Workflow节点：

```text
PlannerAgent

ContextAgent

ResearchAgent

AnalysisAgent

MemoryAgent

ReportAgent
```

---

节点内部：

禁止：

```python
repository.save(...)
```

---

必须：

```python
memory_service.save(...)

tool_service.execute(...)
```

---

# 15. Agent与Service关系

允许：

```text
Agent
↓
ToolService
```

---

允许：

```text
Agent
↓
MemoryService
```

---

禁止：

```text
Agent
↓
Repository
```

---

# 16. Service依赖关系

```text
TaskService
    │
    ▼
TaskRepository


WorkflowService
    │
    ├── WorkflowRunRepository
    ├── TaskRepository
    └── GraphWorkflow


ReportService
    │
    ├── ReportRepository
    └── MemoryService


SourceService
    │
    ├── SourceRepository
    └── MemoryService


ToolService
    │
    ├── ToolRegistry
    └── ToolLogRepository


MemoryService
    │
    └── QdrantStore
```

---

# 17. DTO设计

Service层禁止返回ORM对象。

---

统一：

```python
TaskDTO

ReportDTO

SourceDTO

WorkflowRunDTO
```

---

流程：

```text
ORM

↓

DTO

↓

API Response
```

---

# 18. 异常体系

统一异常基类：

```python
class ServiceError(Exception):
    pass
```

---

子类：

```python
NotFoundError

ValidationError

ConflictError

WorkflowError

MemoryError

ToolExecutionError
```

---

API层统一转换：

```text
HTTP状态码
```

---

# 19. 事务规范

事务边界：

```text
Service层
```

---

Repository：

禁止：

```python
session.commit()
```

---

统一：

```python
UnitOfWork
```

控制。

---

# 20. UnitOfWork

定义：

```python
class UnitOfWork:
    pass
```

---

职责：

```text
事务开启

事务提交

事务回滚
```

---

使用：

```python
async with uow:
    ...
```

---

# 21. 服务注册

统一：

```python
ServiceContainer
```

---

定义：

```python
class ServiceContainer:
    pass
```

---

管理：

```text
TaskService

WorkflowService

ReportService

MemoryService

ToolService
```

---

# 22. 生命周期

应用启动：

```text
创建Repositories

创建Services

注册Container
```

---

应用关闭：

```text
关闭DB连接

关闭Qdrant连接

关闭MCP连接
```

---

# 23. MVP实现范围

第一阶段必须实现：

```text
TaskService

WorkflowService

ReportService

MemoryService

ToolService
```

---

第二阶段实现：

```text
SourceService

MonitoringService
```

---

# 24. 目录规范

```text
backend/app/services/

├── base_service.py

├── task_service.py

├── workflow_service.py

├── report_service.py

├── source_service.py

├── memory_service.py

├── tool_service.py

├── monitoring_service.py

├── dto/

│   ├── task_dto.py
│   ├── report_dto.py
│   ├── source_dto.py
│   └── workflow_run_dto.py

├── exceptions/

│   ├── base.py
│   ├── workflow.py
│   ├── memory.py
│   └── tool.py

└── container/
```

---

# 25. 文档依赖

依赖：

- 07\_数据库设计.md
- 08_API设计.md

后续：

- 10_Frontend设计.md
- 11\_开发实施计划.md

必须遵循本文件定义的服务层架构。
