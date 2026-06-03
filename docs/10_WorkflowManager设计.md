# WorkflowManager设计

---

# 1. 文档目标

定义 WorkflowManager 层设计规范。

WorkflowManager 负责：

```text
不同类型工作流的组织与调度
```

例如：

```text
日报模式

深度研究模式

趋势跟踪模式

用户即时查询模式
```

---

核心目标：

```text
解耦 Workflow 类型
```

避免：

```text
一个巨型 LangGraph
```

承担所有逻辑。

---

# 2. 设计原则

---

## 原则一：Workflow类型解耦

不同任务类型必须拆分为独立 Manager：

```text
DailyWorkflowManager

ResearchWorkflowManager

TrendWorkflowManager
```

---

禁止：

```python
if task_type == "daily":
elif task_type == "research":
elif task_type == "trend":
```

---

## 原则二：共享底层Agent体系

所有 Workflow Manager 共享：

```text
AgentState

ToolRegistry

MemoryService

WorkflowService
```

---

但不共享：

```text
Graph结构
执行策略
调度方式
```

---

## 原则三：Manager不直接操作数据库

禁止：

```python
session.query(...)
```

必须通过：

```text
Service层
```

---

## 原则四：Workflow可组合

允许：

```text
DailyWorkflow = TrendWorkflow + SummaryWorkflow
```

---

## 原则五：支持外部触发

Workflow必须支持：

```text
API触发

定时触发

内部触发（Workflow chain）
```

---

# 3. 系统架构

```text
                API
                 │
                 ▼
         WorkflowService
                 │
                 ▼
        WorkflowManagerRouter
        ┌────────┼────────┐
        │        │        │
        ▼        ▼        ▼
Daily    Research   Trend   Adhoc
Manager   Manager   Manager  Manager
        │
        ▼
   LangGraph Execution
        │
        ▼
   Agent + Tool + Memory
```

---

# 4. WorkflowManagerRouter

---

统一入口：

```python
class WorkflowManagerRouter:
    pass
```

---

职责：

```text
根据task_type选择Manager
```

---

逻辑：

```python
if task.type == "daily":
    return DailyWorkflowManager
elif task.type == "research":
    return ResearchWorkflowManager
elif task.type == "trend":
    return TrendWorkflowManager
```

---

但注意：

```text
只在Router层做分发
```

---

# 5. BaseWorkflowManager

所有Manager统一基类：

```python
class BaseWorkflowManager:
    pass
```

---

定义接口：

```python
async def run(task_id)

async def rerun(task_id)

async def build_graph()
```

---

# 6. DailyWorkflowManager（日报模式）

---

## 目标

自动生成：

```text
每日AI热点摘要
```

---

## 特点

```text
高频

轻量

批处理

多源聚合
```

---

## 执行流程

```text
收集最新Sources
↓
聚合TrendMemory
↓
生成日报摘要
↓
写入Report
↓
更新Memory
```

---

## Graph结构

```text
FetchNewsNode
↓
AggregateNode
↓
SummarizeNode
↓
MemoryUpdateNode
↓
ReportNode
```

---

# 7. ResearchWorkflowManager（深度研究）

---

## 目标

完成：

```text
结构化深度分析报告
```

---

## 特点

```text
多轮

长链推理

工具密集

回环机制
```

---

## 执行流程

```text
Plan
↓
RetrieveSources
↓
DeepAnalysis
↓
IterativeRefinement
↓
MemoryIntegration
↓
ReportGeneration
```

---

## 关键机制：Research Loop

```text
AnalysisNode
   ↓
EvaluationNode
   ↓
if insufficient:
   ↺ back to RetrieveSources
```

---

# 8. TrendWorkflowManager（趋势分析）

---

## 目标

分析：

```text
长期趋势变化
```

---

## 特点

```text
时间序列

Qdrant检索

模式识别
```

---

## 执行流程

```text
FetchHistoricalMemory
↓
ExtractTrendSignals
↓
CompareSnapshots
↓
GenerateTrendReport
↓
StoreTrendMemory
```

---

# 9. AdhocWorkflowManager（即时任务）

---

## 目标

用户即时查询：

```text
“解释MCP是什么”
```

---

## 特点

```text
单轮

低延迟

工具调用驱动
```

---

## 执行流程

```text
PlanNode
↓
ToolExecutionNode
↓
AnswerNode
```

---

# 10. WorkflowManager与LangGraph关系

---

## 原则

```text
Manager = Graph Builder
```

---

Graph真正执行：

```text
LangGraph Runtime
```

---

结构：

```text
WorkflowManager
↓
build_graph()
↓
LangGraph
↓
AgentState Execution
```

---

# 11. Graph执行规范

---

所有Graph必须：

```text
显式定义State流转
```

---

禁止：

```text
隐式全局状态
```

---

State必须：

```text
完全来自 AgentState
```

---

# 12. Research Loop设计（关键）

---

## Loop结构

```text
AnalysisNode
↓
EvaluationNode
↓
ConditionCheck
   ↓
Yes → Continue
   ↓
No  → Back to RetrievalNode
```

---

## 最大迭代次数

```python
max_iterations = 5
```

---

防止：

```text
无限循环
```

---

# 13. WorkflowManager与Service关系

---

允许：

```text
Manager
↓
Service
↓
Repository
```

---

允许：

```text
Manager
↓
ToolService
```

---

禁止：

```text
Manager
↓
Repository
```

---

禁止：

```text
Manager
↓
QdrantClient
```

---

# 14. WorkflowManager目录结构

```text
backend/app/workflows/

├── base/

│   ├── base_manager.py

│   ├── base_graph.py

│   └── state.py

├── routers/

│   └── workflow_router.py

├── daily/

│   ├── manager.py

│   ├── graph.py

├── research/

│   ├── manager.py

│   ├── graph.py

├── trend/

│   ├── manager.py

│   ├── graph.py

├── adhoc/

│   ├── manager.py

│   ├── graph.py
```

---

# 15. Manager接口规范

```python
class BaseWorkflowManager:

    async def run(task_id: str)

    async def rerun(task_id: str)

    def build_graph(self)
```

---

# 16. WorkflowService与Manager关系

```text
WorkflowService
    │
    ▼
WorkflowManagerRouter
    │
    ▼
WorkflowManager
    │
    ▼
LangGraph Execution
```

---

# 17. Workflow类型定义

```python
class WorkflowType:

    DAILY = "daily"

    RESEARCH = "research"

    TREND = "trend"

    ADHOC = "adhoc"
```

---

# 18. 触发方式

---

## API触发

```text
POST /workflows/run
```

---

## 定时触发（未来）

```text
CronJob → WorkflowService
```

---

## 内部触发

```text
Workflow → Workflow
```

---

# 19. 设计收益

---

## Before

```text
一个巨型Graph
所有逻辑混杂
```

---

## After

```text
多个WorkflowManager
职责清晰
可扩展
可测试
```

---

# 20. MVP范围

必须实现：

```text
DailyWorkflowManager

ResearchWorkflowManager

AdhocWorkflowManager
```

---

后续实现：

```text
TrendWorkflowManager
```

---

# 21. 与系统其他层关系

---

## 依赖链

```text
API
↓
WorkflowService
↓
WorkflowManager
↓
LangGraph
↓
Agent + Tool + Memory
```

---

## 不允许跳层

```text
Manager → Repository ❌
Manager → DB ❌
Manager → MCP ❌
```

---

# 22. 文档依赖

依赖：

- 05\_记忆系统设计.md
- 06_MCP设计规范.md
- 09_Service设计.md

后续：

```text
11_前端设计.md
12_系统部署设计.md
```
