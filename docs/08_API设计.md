# API设计

# 1. 文档目标

定义系统API设计规范。

技术栈：

- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- AsyncSession

API职责：

- 任务管理
- 工作流触发
- 报告查询
- 历史检索
- 系统监控

---

# 2. API设计原则

## REST First

采用REST风格。

统一：

```text
/api/v1
```

作为前缀。

---

## Async First

所有接口：

```python
async def
```

实现。

---

## DTO隔离

禁止返回ORM对象。

必须：

```text
ORM
↓
DTO
↓
Response
```

---

## Version First

所有接口必须带版本号。

例如：

```text
/api/v1/tasks
```

---

# 3. API目录结构

```text
backend/app/api/

├── v1/

│   ├── tasks.py
│   ├── reports.py
│   ├── workflows.py
│   ├── memories.py
│   └── health.py

├── dependencies.py

└── router.py
```

---

# 4. 响应规范

统一结构：

```python
class ApiResponse[T]:

    success: bool

    message: str

    data: T | None
```

---

成功：

```json
{
    "success": true,
    "message": "ok",
    "data": {}
}
```

---

失败：

```json
{
    "success": false,
    "message": "task not found",
    "data": null
}
```

---

# 5. Task API

## 创建任务

POST

```text
/api/v1/tasks
```

---

Request

```json
{
    "query": "MCP发展趋势"
}
```

---

Response

```json
{
    "task_id": "uuid"
}
```

---

## 查询任务

GET

```text
/api/v1/tasks/{task_id}
```

---

返回：

```text
任务状态
最新WorkflowRun
```

---

## 获取任务列表

GET

```text
/api/v1/tasks
```

支持：

```text
分页

状态过滤
```

---

# 6. Workflow API

## 启动工作流

POST

```text
/api/v1/workflows/run
```

---

Request

```json
{
    "task_id": "uuid"
}
```

---

作用：

```text
触发一次WorkflowRun
```

---

## 重跑任务

POST

```text
/api/v1/tasks/{task_id}/rerun
```

---

作用：

```text
创建新的WorkflowRun
```

---

## 查询运行记录

GET

```text
/api/v1/tasks/{task_id}/runs
```

---

返回：

```text
全部WorkflowRun
```

---

# 7. Report API

## 获取报告

GET

```text
/api/v1/reports/{report_id}
```

---

返回：

```text
完整Markdown
```

---

## 获取任务报告

GET

```text
/api/v1/tasks/{task_id}/report
```

---

返回：

```text
最新报告
```

---

## 搜索报告

GET

```text
/api/v1/reports/search
```

参数：

```text
query
```

---

调用：

```text
Qdrant report_memory
```

---

# 8. Memory API

## 搜索记忆

GET

```text
/api/v1/memories/search
```

---

参数：

```text
query
```

---

检索：

```text
research_memory

trend_memory

insight_memory

source_memory
```

---

## 获取主题历史

GET

```text
/api/v1/memories/topic/{topic}
```

---

返回：

```text
TrendSnapshot时间序列
```

---

# 9. Source API

## 查询资料

GET

```text
/api/v1/sources
```

---

支持：

```text
task_id

source_type
```

过滤。

---

## 获取资料详情

GET

```text
/api/v1/sources/{source_id}
```

---

# 10. Health API

GET

```text
/api/v1/health
```

---

检查：

```text
PostgreSQL

Qdrant

MCP
```

---

返回：

```json
{
    "postgres": "healthy",
    "qdrant": "healthy",
    "mcp": "healthy"
}
```

---

# 11. OpenAPI规范

自动生成：

```text
/docs

/redoc
```

---

所有接口必须：

```python
response_model=
```

声明。

---

# 12. Service调用链

```text
API
↓
Service
↓
Repository
↓
Database
```

---

禁止：

```text
API
↓
Repository
```

直接访问。

---

# 13. MVP实现范围

第一阶段实现：

- Task API
- Workflow API
- Report API
- Health API

第二阶段：

- Memory API
- Source API

---

# 14. 文档依赖

依赖：

- 07\_数据库设计.md

后续：

- 09_Service设计.md

必须遵循本文件定义的接口规范。
